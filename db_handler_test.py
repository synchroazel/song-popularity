import os
from tqdm import tqdm
from MySQL_connector import *
from spotify_handler import *
from utils import *

"""
You first have to manually create a database within your running instance of MySQL.
"""

sql_handler = MYSQL_connector(user='root', password='magikaio99', host='127.0.0.1', database='dummy_db')

SpotifyClientCredentials(client_id='cc9b11f2d73045ac954aa575677feba5', client_secret='2925a27703d3423b93be7082192e4bb9')

sp_handler = SpotifyHandler()

if __name__ == '__main__':

    all_artists = list()

    for chart in os.listdir('charts_csv'):
        cur = import_chart(f'charts_csv/{chart}')
        all_artists.extend(cur.artist.tolist())

    all_artists = set(all_artists[5:6])  # let's try with a lesser set of artists (no need to stress our DB now)

    # %% Create tables

    # sql_handler.execute_query('create_tables.txt')

    # %% Populate 'artists' table

    for artist in tqdm(all_artists, desc='Updating artists'):
        artist_id = sp_handler.get_artist_id(artist)

        popoularity = sp_handler.get_artist_info(artist_id)['popularity']
        followers = sp_handler.get_artist_info(artist_id)['followers']
        monthly_listeners = sp_handler.get_artist_chart(artist_id)['monthly_listeners']

        to_insert = (artist_id, artist, popoularity, followers, monthly_listeners)

        sql_handler.insert('artists', to_insert)

    # %% Populate 'albums' & 'albums_artists' tables

    from datetime import datetime

    artist_ids = [item[0] for item in sql_handler.select('artists', 'id')]

    for artist_id in tqdm(artist_ids, desc='Updating albums'):

        album_ids = sp_handler.get_artist_albums_ids(artist_id)

        for album_id in album_ids:

            album = sp_handler.get_album_info(album_id)

            try:
                album['release_date'] = datetime.strptime(album['release_date'], '%Y-%m-%d').isoformat()
            except:
                album['release_date'] = datetime.strptime(album['release_date'], '%Y').isoformat()

            to_insert = tuple(album.values())

            sql_handler.insert('albums', to_insert)
            sql_handler.insert('albums_artists', (album_id, artist_id))

    # %% Populate 'track_features', 'tracks' & 'tracks_artists' tables

    album_ids = [item[0] for item in sql_handler.select('albums', 'id')]

    track_ids = list()

    for album_id in tqdm(album_ids, desc='Updating tracks'):

        for track_id in sp_handler.get_songs_ids_by_album(album_id):
            track_feats = sp_handler.get_track_features(track_id)
            track_info = sp_handler.get_track_info(track_id)

            sql_handler.insert('track_features', tuple(track_feats.values()))
            sql_handler.insert('tracks', tuple(
                track_info.values()))

            artist_id = sql_handler.select('albums_artists', 'artist_id', f'album_id=\'{album_id}\'')[0][0]

            sql_handler.insert('tracks_artists', (track_id, artist_id))
            sql_handler.insert('albums_tracks', (track_id, album_id))

    print(f'Databse {sql_handler.database} successfully updated.')
