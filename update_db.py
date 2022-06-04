import argparse
import time

from dateutil.parser import isoparse
from tqdm import tqdm

from handlers.music.spotify_handler import SpotifyHandler
from handlers.mysql.mysql_connector import MYSQL_connector


def get_trending(sp_handler, limit=None):
    artists = list()
    tracks = list()

    top50today = 'https://open.spotify.com/playlist/37i9dQZEVXbIQnj7RRhdSX'
    top50 = sp_handler.get_playlist_tracks(top50today)[:limit]

    for item in top50:
        artists.extend(item['artists'])
        tracks.append(item['track_id'])

    return set(artists), set(tracks)


def update_artists(sql_handler, sp_handler, artists, quiet=True):
    past_artists = [artist[0] for artist in sql_handler.select('artists', 'artist_name')]
    new_artists = artists.difference(past_artists)

    print(f'[INFO] {len(new_artists)} new artists to add to database.')

    if len(new_artists) != 0:

        for artist in tqdm(new_artists, desc='[TQDM] Updating artists'):

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


def update_albums(sql_handler, sp_handler, artists, quiet=True):
    past_albums = [item[0] for item in sql_handler.select('albums', 'id')]
    new_albums = list()

    for artist in artists:
        artist_id = sp_handler.get_artist_id(artist)
        new_albums.extend(sp_handler.get_artist_albums_ids(artist_id))

    new_albums = set(new_albums).difference(past_albums)

    print(f'[INFO] {len(new_albums)} new albums to add to database.')

    if len(new_albums) != 0:

        for album_id in tqdm(new_albums, desc='[TQDM] Updating albums'):

            if not quiet:
                print(f'[INFO] adding album: {album_id}')

            album = sp_handler.get_album_info(album_id)

            album['release_date'] = isoparse(album['release_date']).strftime('%Y-%m-%d')

            sql_handler.insert('albums', tuple(album.values()))
            sql_handler.insert('albums_artists', (album_id, artist_id))

            time.sleep(1)

        print(f'[INFO] {len(new_albums)} albums info successfully added to database.')


def update_tracks(sql_handler, sp_handler, artists, tracks, quiet=True):
    past_tracks = [item[0] for item in sql_handler.select('tracks', 'id')]
    new_albums = list()
    new_tracks = list()

    for artist in artists:
        artist_id = sp_handler.get_artist_id(artist)
        new_albums.extend(sp_handler.get_artist_albums_ids(artist_id))

    for album_id in new_albums:
        new_tracks.extend(sp_handler.get_songs_ids_by_album(album_id))

    new_tracks = set(new_tracks).difference(past_tracks)
    new_tracks = new_tracks.union(tracks)

    print(f'[INFO] {len(new_tracks)} new tracks to add to database.')

    if len(new_tracks) != 0:

        for track_id in tqdm(new_tracks, desc='[TQDM] Updating tracks'):

            if (track_id,) not in sql_handler.select('tracks', 'id'):

                if not quiet:
                    print(f'[INFO] adding track: {track_id}')

                track_feats = sp_handler.get_track_features(track_id)
                track_info = sp_handler.get_track_info(track_id)

                if track_info != None and track_feats != None:
                    sql_handler.insert('track_features', tuple(track_feats.values()))
                    sql_handler.insert('tracks', tuple(track_info.values()))

                    artist_id = sql_handler.select('albums_artists', 'artist_id', f'album_id=\'{album_id}\'')[0][0]

                    sql_handler.insert('tracks_artists', (track_id, artist_id))
                    sql_handler.insert('albums_tracks', (track_id, album_id))

                    time.sleep(1)

        print(f'[INFO] {len(new_tracks)} tracks info successfully added to database.')


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="Update a MySQL database with songs information.")
    arg_parser.add_argument("--mysql_db", type=str, required=True, default=None, help="The MySQL database")
    arg_parser.add_argument("--mysql_host", type=str, required=True, default=None, help="The MySQL host")
    arg_parser.add_argument("--mysql_user", type=str, required=True, default=None, help="The MySQL username")
    arg_parser.add_argument("--mysql_password", type=str, required=True, default=None, help="The MySQL password")
    arg_parser.add_argument("--skipto", type=str, choices=['albums', 'tracks'], required=False, default=None,
                            help="Skip to specific phase of ingestion")

    args = arg_parser.parse_args()

    sql_handler = MYSQL_connector(host=args.mysql_host,
                                  user=args.mysql_user,
                                  password=args.mysql_password,
                                  database=args.mysql_db)

    sp_handler = SpotifyHandler()

    new_artists, new_tracks = get_trending(sp_handler)

    if args.skipto == 'tracks':
        print(f'[INFO] Skipping to tracks ingestion phase.')
        update_tracks(sql_handler, sp_handler, new_artists, new_tracks, quiet=False)

    if args.skipto == 'albums':
        print(f'[INFO] Skipping to albums ingestion phase.')
        update_albums(sql_handler, sp_handler, new_artists)
        update_tracks(sql_handler, sp_handler, new_artists, new_tracks)

    if args.skipto == None:
        update_artists(sql_handler, sp_handler, new_artists)
        update_albums(sql_handler, sp_handler, new_artists)
        update_tracks(sql_handler, sp_handler, new_artists, new_tracks)

    print(f'[INFO] Database {args.mysql_db} successfully updated.')
