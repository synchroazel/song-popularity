import argparse
import os
import time

import mysql.connector
from dateutil.parser import isoparse
from tqdm import tqdm

from handlers.music.spotify_handler import SpotifyHandler
from handlers.mysql.mysql_connector import MYSQL_connector
from handlers.utils import import_chart


def check_database(db_name, host, user, password):
    mydb = mysql.connector.connect(host=host, user=user, password=password)

    mycursor = mydb.cursor()
    mycursor.execute("SHOW DATABASES")

    for db in mycursor:
        if args.mysql_db in db:
            return True

    return False


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


def check_tables(sql_handler):
    r = sql_handler.execute_query('sql_queries/check_tables.sql')
    return r == [('albums',), ('artists',), ('tracks',), ('track_features',), ('albums_tracks',), ('tracks_artists',)]


def create_tables(sql_handler):
    sql_handler.execute_query('sql_queries/create_tables.sql')
    print('[INFO] Tables successfully created.')


def past_trending_artists(charts_path='music_charts', limit=None):
    artists = list()

    for chart in os.listdir(charts_path):
        cur = import_chart(os.path.join(charts_path, chart))
        artists.extend(cur.artist.tolist())

    return set(artists[:limit])


def ingest_artists(sql_handler, sp_handler, artists, quiet=True):
    for artist in tqdm(artists, desc='[TQDM] Updating artists'):

        artist_id = sp_handler.get_artist_id(artist)

        if not quiet:
            print(f'[INFO] adding artist: {artist} | id: {artist_id}')

        if artist_id != None:

            monthly_listeners = sp_handler.get_monthly_listeners(artist_id)

            if monthly_listeners != None:

                popoularity = sp_handler.get_artist_info(artist_id)['popularity']
                followers = sp_handler.get_artist_info(artist_id)['followers']

                sql_handler.insert('artists', (artist_id, artist, popoularity, followers, monthly_listeners))

                time.sleep(1)

    print(f'[INFO] {len(artists)} artists info successfully added to database.')


def ingest_albums(sql_handler, sp_handler, quiet=True):
    artist_ids = [item[0] for item in sql_handler.select('artists', 'id')]

    n_album = 0

    for artist_id in tqdm(artist_ids, desc='[TQDM] Updating albums'):

        album_ids = sp_handler.get_artist_albums_ids(artist_id)

        for album_id in album_ids:

            if not quiet:
                print(f'[INFO] adding album: {album_id} | from artist: {artist_id}')

            album = sp_handler.get_album_info(album_id)

            album['release_date'] = isoparse(album['release_date']).strftime('%Y-%m-%d')

            sql_handler.insert('albums', tuple(album.values()))
            sql_handler.insert('albums_artists', (album_id, artist_id))

            n_album += 1

            time.sleep(1)

    print(f'[INFO] {n_album} albums info successfully added to database.')


def ingest_tracks(sql_handler, sp_handler, quiet=True):
    album_ids = [item[0] for item in sql_handler.select('albums', 'id')]

    n_tracks = 0

    for album_id in tqdm(album_ids, desc='[TQDM] Updating tracks'):

        track_ids = sp_handler.get_songs_ids_by_album(album_id)

        for track_id in track_ids:

            if (track_id,) not in sql_handler.select('tracks', 'id'):

                if not quiet:
                    print(f'[INFO] adding track: {track_id} | from album: {album_id}')

                track_feats = sp_handler.get_track_features(track_id)
                track_info = sp_handler.get_track_info(track_id)

                if track_info != None and track_feats != None:

                    artist_id = sp_handler.get_track_artist(track_id)
                    # artist_id = sql_handler.select('albums_artists', 'artist_id', f'album_id=\'{album_id}\'')[0][0]

                    if artist_id != None:

                        sql_handler.insert('track_features', tuple(track_feats.values()))
                        sql_handler.insert('tracks', tuple(track_info.values()))

                        sql_handler.insert('tracks_artists', (track_id, artist_id))
                        sql_handler.insert('albums_tracks', (track_id, album_id))

                        n_tracks += 1

                        time.sleep(1)

    print(f'[INFO] {n_tracks} tracks info successfully added to database.')


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="Initialize a MySQL database with songs information.")
    arg_parser.add_argument("--mysql_db", type=str, required=True, default=None, help="The MySQL database")
    arg_parser.add_argument("--mysql_host", type=str, required=True, default=None, help="The MySQL host")
    arg_parser.add_argument("--mysql_user", type=str, required=True, default=None, help="The MySQL username")
    arg_parser.add_argument("--mysql_password", type=str, required=True, default=None, help="The MySQL password")
    arg_parser.add_argument("--limit", type=int, required=False, default=-1,
                            help="Limit the number of artists to import")
    arg_parser.add_argument("--skipto", type=str, choices=['albums', 'tracks'], required=False, default=None,
                            help="Skip to specific phase of ingestion")

    args = arg_parser.parse_args()

    create_database(db_name=args.mysql_db, host=args.mysql_host, user=args.mysql_user, password=args.mysql_password)

    sql_handler = MYSQL_connector(host=args.mysql_host,
                                  user=args.mysql_user,
                                  password=args.mysql_password,
                                  database=args.mysql_db)

    try:
        create_tables(sql_handler)
    except:
        pass

    sp_handler = SpotifyHandler()

    artists = past_trending_artists(limit=args.limit)

    if args.skipto == 'tracks':
        print(f'[INFO] Skipping to tracks ingestion phase.')
        ingest_tracks(sql_handler, sp_handler)

    if args.skipto == 'albums':
        print(f'[INFO] Skipping to albums ingestion phase.')
        ingest_albums(sql_handler, sp_handler)
        ingest_tracks(sql_handler, sp_handler)

    if args.skipto == None:
        ingest_artists(sql_handler, sp_handler, artists)
        ingest_albums(sql_handler, sp_handler)
        ingest_tracks(sql_handler, sp_handler)

    print(f'[INFO] Database {args.mysql_db} successfully updated.')
