import requests
import spotipy
from bs4 import BeautifulSoup
from spotipy.oauth2 import SpotifyClientCredentials

credentials = SpotifyClientCredentials(client_id='cc9b11f2d73045ac954aa575677feba5',
                                       client_secret='2925a27703d3423b93be7082192e4bb9')


class SpotifyHandler:

    def __init__(self, credentials):
        self.sp = spotipy.Spotify(client_credentials_manager=credentials)

    def get_top_tracks(self, artist_url):
        '''
        Get an artist's monthly listeners and their top 5 tracks.
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


# %% TESTING

from pprint import pprint  # just for testing purposes, not in the final module

url1 = 'https://open.spotify.com/artist/26VFTg2z8YR0cCuwLzESi2'  # Halsey spotify page
url2 = 'https://open.spotify.com/artist/1vCWHaC5f2uS3yhpwWbIA6'  # AVICII spotify page

sp = SpotifyHandler(credentials)

pprint(sp.get_top_tracks(url1))
