import os
import time
from tqdm import tqdm
from MySQL_connector import *
from spotify_handler import *
from utils import *

"""
You first have to manually create a database within your running instance of MySQL.
"""

sql_handler = MYSQL_connector(user='root', password='magikaio99', host='127.0.0.1', database='dummy_db')

sp_handler = SpotifyHandler()

if __name__ == '__main__':

    all_artists = list()

    for chart in os.listdir('charts_csv'):
        cur = import_chart(f'charts_csv/{chart}')
        all_artists.extend(cur.artist.tolist())

    all_artists = set(all_artists[:15])  # let's try with a lesser set of artists (no need to stress our DB now)

    # sql_handler.execute_query('DROP TABLE `dummy_db`.`albums`, `dummy_db`.`albums_artists`, `dummy_db`.`albums_tracks`, `dummy_db`.`artists`, `dummy_db`.`track_features`, `dummy_db`.`tracks`, `dummy_db`.`tracks_artists`')

    # %% Create tables

    # sql_handler.execute_query('create_tables.txt')

    # %% Populate 'artists' table

    all_artists = all_artists.difference(
        set([artist[0] for artist in sql_handler.select('artists', 'artist_name')])
    )

    for artist in tqdm(all_artists, desc='Updating artists'):

        artist_id = sp_handler.get_artist_id(artist)

        if artist_id != None:

            # print(f'\nArtist {artist} | id {artist_id}')

            monthly_listeners = sp_handler.get_monthly_listeners(artist_id)

            if monthly_listeners != 0:
                popoularity = sp_handler.get_artist_info(artist_id)['popularity']
                followers = sp_handler.get_artist_info(artist_id)['followers']

                to_insert = (artist_id, artist, popoularity, followers, monthly_listeners)

                sql_handler.insert('artists', to_insert)

    # %% Populate 'albums' & 'albums_artists' tables

    from datetime import datetime

    # artist_ids = [item[0] for item in sql_handler.select('artists', 'id')]

    all_artists_ids = [sp_handler.get_artist_id(artist_name) for artist_name in all_artists]

    for artist_id in tqdm(all_artists_ids, desc='Updating albums'):

        album_ids = sp_handler.get_artist_albums_ids(artist_id)

        new_albums = set(album_ids).difference(
            set([album[0] for album in sql_handler.select('albums', 'id')])
        )

        for album_id in new_albums:

            album = sp_handler.get_album_info(album_id)

            try:
                album['release_date'] = datetime.strptime(album['release_date'], '%Y-%m-%d').isoformat()
            except:
                try:
                    album['release_date'] = datetime.strptime(album['release_date'], '%Y-%m').isoformat()
                except:
                    album['release_date'] = datetime.strptime(album['release_date'], '%Y').isoformat()

            to_insert = tuple(album.values())

            sql_handler.insert('albums', to_insert)
            sql_handler.insert('albums_artists', (album_id, artist_id))
            time.sleep(2)

    # %% Populate 'track_features', 'tracks' & 'tracks_artists' tables

    album_ids = [item[0] for item in sql_handler.select('albums', 'id')]

    track_ids = list()

    for album_id in tqdm(album_ids, desc='Updating tracks'):

        track_ids = sp_handler.get_songs_ids_by_album(album_id)

        track_ids = set(track_ids).difference(
            set([track[0] for track in sql_handler.select('tracks', 'id')])
        )

        for track_id in track_ids:
            track_feats = sp_handler.get_track_features(track_id)
            track_info = sp_handler.get_track_info(track_id)

            sql_handler.insert('track_features', tuple(track_feats.values()))
            sql_handler.insert('tracks', tuple(
                track_info.values()))

            artist_id = sql_handler.select('albums_artists', 'artist_id', f'album_id=\'{album_id}\'')[0][0]

            sql_handler.insert('tracks_artists', (track_id, artist_id))
            sql_handler.insert('albums_tracks', (track_id, album_id))
            time.sleep(1)

    print(f'Database {sql_handler.database} successfully updated.')
