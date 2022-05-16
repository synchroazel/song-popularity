# SET SPOTIPY_CLIENT_ID='your-spotify-client-id'
# SET SPOTIPY_CLIENT_SECRET='your-spotify-client-secret'
# SET SPOTIPY_REDIRECT_URI='your-app-redirect-url'

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from pprint import pprint

cid = "47fe30024ef2462693f4795582243f73"
secret = "3ba8979a36a1467a92d77a7d3ae5badb"


client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)
track = sp.track("5Iy2Jj87Ha0C0IBlNE1I4y?si=5e5d126e11244d67")
#pprint(track)
#print(len(track['album']['artists']))
artist = "Halsey"
searchQuery = "Colors"

searchResults = sp.search(q="artist:" + artist + " track:" + searchQuery, type="track")

#IF IT in available_markets

#pprint(searchResults)
#in id is the final line for the artist uri
#print(len(searchResults['tracks']['items']))
#conf = ("47fe30024ef2462693f4795582243f73", "3ba8979a36a1467a92d77a7d3ae5badb", "http://localhost/")

artist_name = "Breaking Benjamin"
song_name = "Evil angel"
songs = sp.search(q="artist:" + artist_name + " track:" + song_name, type="track")
#pprint(songs['tracks']['items'][0]['album']['id'])

artist = sp.artist("5BtHciL0e0zOP7prIHn3pP")
#pprint(artist)

albums_info = sp.artist_albums("5BtHciL0e0zOP7prIHn3pP", limit = 50)
pprint(albums_info)