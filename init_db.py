import argparse
import os
import random
import time

import mysql.connector
import pandas as pd
from dateutil.parser import isoparse
from tqdm import tqdm

from handlers.music.spotify_handler import SpotifyHandler
from handlers.mysql.mysql_connector import MYSQL_connector


def import_chart(filepath):
    chart = pd.read_csv(filepath, header=1)
    chart.URL = chart.URL.str.replace('https://open.spotify.com/track/', '', regex=True)
    chart = chart.rename(columns={'URL': 'track_id',
                                  'Streams': 'streams',
                                  'Artist': 'artist',
                                  'Track Name': 'track_name'})

    return chart.drop('Position', axis=1)


def create_database(db_name, host, user, password):
    mydb = mysql.connector.connect(host=host, user=user, password=password)

    mycursor = mydb.cursor()

    try:
        mycursor.execute(f"CREATE DATABASE `{db_name}`")
        print(f'[INFO] Database {db_name} successfully created.')
        mydb.commit()
    except mysql.connector.errors.DatabaseError:
        print(f'[INFO] A database named {db_name} already exist.')

    mydb.close()
    return


def create_tables(sql_handler):
    try:
        sql_handler.execute_query('sql_queries/create_tables.sql')
        print('[INFO] Tables successfully created.')
    except:
        print('[INFO] Tables already exists.')


def past_trending_artists(charts_path='music_charts', limit=-1):
    artists = list()

    for chart in os.listdir(charts_path):
        cur = import_chart(os.path.join(charts_path, chart))
        artists.extend(cur.artist.tolist())

    artists = set(artists)

    return list(artists)[:limit]


def ingest_artists(sql_handler, sp_handler, artists, quiet=True):
    n_artists = 0

    for artist in tqdm(artists, desc='[TQDM] Updating artists'):

        artist_id = sp_handler.get_artist_id(artist)

        if artist_id is not None:

            if (artist_id,) not in sql_handler.select('artists', 'id'):

                monthly_listeners = sp_handler.get_monthly_listeners(artist_id)

                if monthly_listeners is not None:

                    if not quiet:
                        print(f'[INFO] Adding artist {artist} with id {artist_id}')

                    popularity = sp_handler.get_artist_info(artist_id)['popularity']
                    followers = sp_handler.get_artist_info(artist_id)['followers']

                    sql_handler.insert('artists', (artist_id, artist, popularity, followers, monthly_listeners))

                    n_artists += 1

                    time.sleep(2)

    print(f'[INFO] {n_artists} artists info successfully added to database.')


def ingest_albums(sql_handler, sp_handler, artists, quiet=True):
    n_album = 0

    for artist in tqdm(artists, desc='[TQDM] Updating albums'):

        artist_id = sp_handler.get_artist_id(artist)

        if artist_id is not None:

            album_ids = sp_handler.get_artist_albums(artist_id)

            for album_id in album_ids:

                if (album_id,) not in sql_handler.select('albums', 'id'):

                    album = sp_handler.get_album_info(album_id)

                    album['release_date'] = isoparse(album['release_date']).strftime('%Y-%m-%d')

                    # Check `album_id` belongs to `artist_id`
                    if album_id in sp_handler.get_artist_albums(artist_id):

                        if not quiet:
                            print(f'[INFO] adding album {album_id} from artist {artist_id}')

                        sql_handler.insert('albums', tuple(album.values()))
                        sql_handler.insert('albums_artists', (album_id, artist_id))

                        n_album += 1

                        time.sleep(2)

    print(f'[INFO] {n_album} albums info successfully added to database.')


def ingest_tracks(sql_handler, sp_handler, artists, quiet=True):
    n_tracks = 0

    for artist in tqdm(artists, desc='[TQDM] Updating tracks'):

        artist_id = sp_handler.get_artist_id(artist)

        if artist_id is not None:

            album_ids = sp_handler.get_artist_albums(artist_id)

            for album_id in album_ids:

                track_ids = sp_handler.get_album_tracks(album_id)

                for track_id in track_ids:

                    if track_id is not None:

                        if (track_id,) not in sql_handler.select('tracks', 'id'):

                            if random.choices([0, 1], [3 / 4, 1 / 4])[0]:

                                track_feats = sp_handler.get_track_features(track_id)
                                track_info = sp_handler.get_track_info(track_id)

                                if track_info != None and track_feats != None and artist_id != None:

                                    if not quiet:
                                        print(f'[INFO] adding track {track_id} from album {album_id}')

                                    sql_handler.insert('track_features', tuple(track_feats.values()))
                                    sql_handler.insert('tracks', tuple(track_info.values()))

                                    sql_handler.insert('tracks_artists', (track_id, artist_id))
                                    sql_handler.insert('albums_tracks', (track_id, album_id))

                                    n_tracks += 1

                                    time.sleep(2)

    print(f'[INFO] {n_tracks} tracks info successfully added to database.')


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="Initialize a MySQL database with songs information.")
    arg_parser.add_argument("--mysql_db", type=str, required=True, default=None, help="The MySQL database")
    arg_parser.add_argument("--mysql_host", type=str, required=True, default=None, help="The MySQL host")
    arg_parser.add_argument("--mysql_user", type=str, required=True, default=None, help="The MySQL username")
    arg_parser.add_argument("--mysql_password", type=str, required=True, default=None, help="The MySQL password")
    arg_parser.add_argument("--limit", type=int, required=False, default=-1, help="Limit the number of artists to import")

    args = arg_parser.parse_args()

    create_database(db_name=args.mysql_db,
                    host=args.mysql_host,
                    user=args.mysql_user,
                    password=args.mysql_password)

    sql = MYSQL_connector(host=args.mysql_host,
                          user=args.mysql_user,
                          password=args.mysql_password,
                          database=args.mysql_db)

    spt = SpotifyHandler()

    create_tables(sql)

    past_artists = past_trending_artists(limit=args.limit)

    ingest_artists(sql, spt, past_artists)
    ingest_albums(sql, spt, past_artists)
    ingest_tracks(sql, spt, past_artists)
