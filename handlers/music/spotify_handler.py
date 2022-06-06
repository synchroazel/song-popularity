import requests
import spotipy
from bs4 import BeautifulSoup

from secrets import sp_credentials


class SpotifyHandler:

    def __init__(self, credentials=sp_credentials):
        self.sp = spotipy.Spotify(client_credentials_manager=credentials)

    def get_artist_id(self, artist_name):
        r = self.sp.search(artist_name, type="artist", limit=10)
        for item in r['artists']['items']:
            if item['name'] == artist_name:
                return item['id']
        return None

    def get_album_info(self, album_id):
        r = self.sp.album(album_id)
        return {
            'album_id': r['id'],
            'album_name': r['name'],
            'release_date': r['release_date']
        }

    def get_track_info(self, track_id):
        r = self.sp.track(track_id)
        return {
            'track_id': r['id'],
            'track_name': r['name'],
            'track_popularity': r['popularity']
        }

    def get_track_artist(self, track_id):
        r = self.sp.track(track_id)
        return r['artists'][0]['id']

    def get_track_album(self, track_id):
        r = self.sp.track(track_id)
        return r['album']['id']

    def get_track_genres(self, track_id):
        r = self.sp.track(track_id)

        if self.sp.album(r['album']['id'])['genres'].__len__() != 0:
            return self.sp.album(r['album']['id'])['genres']
        else:
            return self.sp.artist(r['artists'][0]['id'])['genres']

    def get_track_features(self, track_id):
        r = self.sp.audio_features(track_id)[0]

        if r is None:
            return None

        excluded = ('uri', 'type', 'analysis_url', 'track_href', 'id')
        features = {key: value for key, value in r.items() if key not in excluded}

        ret = {'track_id': track_id}
        ret.update(features)
        return ret

    def get_analysis_by_track_id(self, track_id):
        r = self.sp.audio_analysis(track_id)

        excluded = ('codestring', 'code_version',
                    'echoprintstring', 'echoprint_version',
                    'synchstring', 'synch_version',
                    'rhythmstring', 'rhythm_version')

        return {key: value for key, value in r['track'].items() if key not in excluded}

    def get_monthly_listeners(self, artist_id):

        artist_url = 'https://open.spotify.com/artist/' + artist_id

        r = requests.get(artist_url)
        soup = BeautifulSoup(r.text, features="html.parser")

        monthly_listeners = soup.findAll('div', {'class': 'Type__TypeElement-goli3j-0'})
        monthly_listeners = [content for content in monthly_listeners if 'monthly listeners' in content.text]

        if len(monthly_listeners) != 0:
            return int(monthly_listeners[0].text.split(' ')[0].replace(',', ''))
        else:
            return None

    def get_artist_albums(self, artist_id):
        albums_info = self.sp.artist_albums(artist_id, limit=50, album_type=['album', 'single'])
        ret = []
        for item in albums_info['items']:
            ret.append(item['id'])
        return ret

    def get_album_tracks(self, album_id):
        songs = self.sp.album_tracks(album_id, limit=50)
        ret = []
        for song in songs['items']:
            ret.append(song["id"])
        return ret

    def get_track_id(self, track_name, artist_name):
        info = self.sp.search(q="artist:" + artist_name + " track:" + track_name, type="track")
        return info['tracks']['items'][0]['id']

    def get_artist_info(self, artist_id):
        artist = self.sp.artist(artist_id)
        return {
            "followers": int(artist['followers']['total']),
            "popularity": int(artist["popularity"])
        }

    def get_playlist_tracks(self, playlist_id):
        plst_tracks = self.sp.playlist_items(playlist_id=playlist_id)
        ret = list()
        for song in plst_tracks['items']:
            ret.append(
                {
                    'track_name': song['track']['name'],
                    'track_id': song['track']['id'],
                    'artists': [artist['name'] for artist in song['track']['artists']]
                }
            )
        return ret
