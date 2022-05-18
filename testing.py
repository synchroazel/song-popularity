from pprint import pprint
from spotify_handler import *

sp = SpotifyHandler(credentials)

# %% TESTING .get_top_tracks

pprint(sp.get_top_tracks_by_artist_url('https://open.spotify.com/artist/1vCWHaC5f2uS3yhpwWbIA6'))

# %% TESTING .get_artist_info

pprint(sp.get_artist_info("26VFTg2z8YR0cCuwLzESi2"))

# %% TESTING .get_song_id_by_name_and_artist

pprint(sp.get_song_id_by_name_and_artist("Impossible", "James Arthur"))

# %% TESTING .get_songs_ids_by_album

pprint(sp.get_songs_ids_by_album("3pfiqQljVzq48rfw0bNdpz"))

# %% TESTING .get_artist_albums_ids

pprint(sp.get_artist_albums_ids("1vCWHaC5f2uS3yhpwWbIA6"))

# %% TESTING .get_audio_analysis

pprint(sp.get_analysis_by_track_id('0vFOzaXqZHahrZp6enQwQb'))

# %% TESTING .get_playlist_tracks

top10_italia = '37i9dQZEVXbIQnj7RRhdSX'

pprint(sp.get_playlist_tracks(top10_italia))