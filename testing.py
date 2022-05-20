from pprint import pprint

from spotify_handler import *
from youtube_handler import *

sp = SpotifyHandler(credentials)
yt = YoutubeHandler(api_key)

# %% TESTING .get_genres_by_track_id

pprint(sp.get_genres_by_track_id('0vFOzaXqZHahrZp6enQwQb'))

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

# %% TESTING .get_analysis_by_track_id

pprint(sp.get_analysis_by_track_id('0vFOzaXqZHahrZp6enQwQb'))

# %% TESTING .get_features_by_track_id

pprint(sp.get_features_by_track_id('0vFOzaXqZHahrZp6enQwQb'))

# %% TESTING .get_playlist_tracks

pprint(sp.get_playlist_tracks('37i9dQZF1DWUJcZpQ1337Z'))

# %% TESTING .search_by_id()

song_id1 = 'rLoGGMbF-YQ'  # Jovanotti - I love you baby
song_id2 = 'MA_5P3u0apQ'  # Mahmood & Blanco - Brividi

pprint(yt.search_by_id(song_id1))

# %% TESTING .search_by_keyword

pprint(yt.search_by_keyword('Jovanotti', 100))

# %% TESTING .search_song

pprint(yt.search_song('I love you baby', 'Jovanotti'))

# %% TESTING .search_by_id

pprint(yt.search_by_id('rLoGGMbF-YQ'))
