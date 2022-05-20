import requests
import spotipy
from bs4 import BeautifulSoup
from spotipy.oauth2 import SpotifyClientCredentials

credentials = SpotifyClientCredentials(client_id='cc9b11f2d73045ac954aa575677feba5',
                                       client_secret='2925a27703d3423b93be7082192e4bb9')


class SpotifyHandler:

    def __init__(self, credentials=credentials):
        self.sp = spotipy.Spotify(client_credentials_manager=credentials)

    def get_genres_by_track_id(self, track_id):
        r = self.sp.track(track_id)

        if self.sp.album(r['album']['id'])['genres'].__len__() != 0:
            return self.sp.album(r['album']['id'])['genres']
        else:
            print('debug')
            return self.sp.artist(r['artists'][0]['id'])['genres']

    def get_features_by_track_id(self, track_id):
        return self.sp.audio_features(track_id)[0]

    def get_analysis_by_track_id(self, track_id):
        r = self.sp.audio_analysis(track_id)

        excluded = ('codestring', 'code_version',
                    'echoprintstring', 'echoprint_version',
                    'synchstring', 'synch_version',
                    'rhythmstring', 'rhythm_version')

        return {key: value for key, value in r['track'].items() if key not in excluded}

    def get_top_tracks_by_artist_url(self, artist_url):
        r = requests.get(artist_url)
        soup = BeautifulSoup(r.text, features="html5lib")

        monthly_listeners = soup.findAll('div', {'class': 'Type__TypeElement-goli3j-0 edDNNU ovtJYocZljdWcU1FLBL5'})[0]
        monthly_listeners = int(monthly_listeners.text.split(' ')[0].replace(',', ''))

        top_tracks = list()
        for item in soup.findAll('div', {'class': 'Row__Container-sc-brbqzp-0 jKreJT'}):
            top_tracks.append((item.findAll('span')[0].text,
                               int(item.findAll('span')[2].text.replace(',', ''))))

        return {'monthly_listeners': monthly_listeners,
                'top_tracks': top_tracks}

    def get_artist_albums_ids(self, artist_id):  # NOT SURE HERE if we should do some filtering or this tokenization???
        albums_info = self.sp.artist_albums(artist_id, limit=50)
        ret = []
        for item in albums_info['items']:
            ret.append(item['id'])
        return ret  # a list with albums ids

    def get_songs_ids_by_album(self, album_id):
        songs = self.sp.album_tracks(album_id, limit=50)
        ret = []
        for song in songs['items']:
            ret.append(song["id"])
        return ret

    def get_song_id_by_name_and_artist(self, track_name, artist_name):
        info = self.sp.search(q="artist:" + artist_name + " track:" + track_name, type="track")
        return info['tracks']['items'][0]['album']['id']

    def get_artist_info(self, artist_id):
        artist = self.sp.artist(artist_id)
        return {"followers": int(artist['followers']['total']),
                "popularity_index": int(artist["popularity"])}

    def get_playlist_tracks(self, playlist_id):
        plst_tracks = self.sp.playlist_items(playlist_id=playlist_id)
        ret = list()
        for song in plst_tracks['items']:
            ret.append({
                'track_name': song['track']['name'],
                'track_id': song['track']['id'],
                'artists': [artist['name'] for artist in song['track']['artists']]
            })
        return ret
