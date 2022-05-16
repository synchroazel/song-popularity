import requests
import spotipy
from bs4 import BeautifulSoup
from spotipy.oauth2 import SpotifyClientCredentials

from pprint import pprint  # just for testing purposes, not in the final module

credentials = SpotifyClientCredentials(client_id='cc9b11f2d73045ac954aa575677feba5',
                                       client_secret='2925a27703d3423b93be7082192e4bb9')


class SpotifyHandler:

    def __init__(self, credentials=credentials):
        self.sp = spotipy.Spotify(client_credentials_manager=credentials)

    def get_audio_analysis(self, track_id):
        '''
        Get a number of features from a track, given its id.
        :param track_id: track_id of the song to analyse
        :return: dict with a number of features regarding given song
        '''

        r = self.sp.audio_analysis('0vFOzaXqZHahrZp6enQwQb')

        excluded = ('codestring', 'code_version',
                    'echoprintstring', 'echoprint_version',
                    'synchstring', 'synch_version',
                    'rhythmstring', 'rhythm_version')

        return {key: value for key, value in r['track'].items() if key not in excluded}

    def get_top_tracks(self, artist_url):
        '''
        Get an artist's monthly listeners and their top 5 tracks.
        :param artist_url: url of the artist's spotify page
        :return: dict with 'monthly_listeners' and tuples (track, views) of top-5 tracks
        '''

        r = requests.get(artist_url)

        soup = BeautifulSoup(r.text)

        monthly_listeners = soup.findAll('div', {'class': 'Type__TypeElement-goli3j-0 edDNNU ovtJYocZljdWcU1FLBL5'})[0]
        monthly_listeners = int(monthly_listeners.text.split(' ')[0].replace(',', ''))

        top_tracks = list()

        for item in soup.findAll('div', {'class': 'Row__Container-sc-brbqzp-0 jKreJT'}):
            top_tracks.append((item.findAll('span')[0].text,
                               int(item.findAll('span')[2].text.replace(',', ''))))

        return {'monthly_listeners': monthly_listeners,
                'top_tracks': top_tracks}

    def get_artist_albums_ids(self, artist_id): # NOT SURE HERE if we should do some filtering or this tokenization???
        albums_info = self.sp.artist_albums(artist_id, limit = 50)
        ret = []
        for item in albums_info['items']:
            ret.append(item['id'])
        return ret #a list with albums ids

    def get_songs_ids_by_album(self, album_id):
        songs = self.sp.album_tracks(album_id, limit = 50)
        ret = []
        for song in songs['items']:
            ret.append(song["id"])
        return ret

    def get_song_id_by_name_and_artist(self, song_name, artist_name):
        info = self.sp.search(q="artist:" + artist_name + " track:" + song_name, type="track")
        return info['tracks']['items'][0]['album']['id']

    def get_artist_info(self, artist_id):
        artist = self.sp.artist(artist_id)
        return {"followers": int(artist['followers']['total']),
                "popularity_index": int(artist["popularity"])}


# %% TESTING .get_top_tracks()

url1 = 'https://open.spotify.com/artist/26VFTg2z8YR0cCuwLzESi2'  # Halsey spotify page
url2 = 'https://open.spotify.com/artist/1vCWHaC5f2uS3yhpwWbIA6'  # AVICII spotify page

sp = SpotifyHandler(credentials)

pprint(
    sp.get_top_tracks(url1)
)

# %% TESTING .get_artist_info
pprint(sp.get_artist_info("26VFTg2z8YR0cCuwLzESi2"))

print()
# %% TESTING .get_song_id_by_name_and_artist
pprint(sp.get_song_id_by_name_and_artist("Impossible", "James Arthur"))

print()
# %% TESTING .get_songs_ids_by_album
pprint(sp.get_songs_ids_by_album("3pfiqQljVzq48rfw0bNdpz"))

print()
# %% TESTING .get_artist_albums_ids
pprint(sp.get_artist_albums_ids("1vCWHaC5f2uS3yhpwWbIA6"))

print()
# %% TESTING .get_audio_analysis()

track_id = '0vFOzaXqZHahrZp6enQwQb'  # Money - Pink Floyd

sp = SpotifyHandler(credentials)

pprint(
    sp.get_audio_analysis(track_id)
)