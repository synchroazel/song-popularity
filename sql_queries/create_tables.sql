CREATE TABLE IF NOT EXISTS albums(
id VARCHAR(30) PRIMARY KEY,
album_name VARCHAR(100),
release_date DATE
);

CREATE TABLE IF NOT EXISTS artists(
id VARCHAR(30) PRIMARY KEY,
artist_name VARCHAR(100),
artist_popularity INT,
followers INT,
monthly_listeners INT
);

CREATE TABLE IF NOT EXISTS track_features(
track_id VARCHAR(30) PRIMARY KEY,
danceability DECIMAL(5,3),
energy DECIMAL(5,3),
`key` INT,
loudness DECIMAL(5,3),
mode INT,
speechiness DECIMAL(5,3),
acousticness DECIMAL(5,3),
instrumentalness DECIMAL(5,3),
liveness DECIMAL(5,3),
valence DECIMAL(5,3),
tempo DECIMAL(10,3),
duration_ms INT,
time_signature INT
);

CREATE TABLE IF NOT EXISTS tracks(
id VARCHAR(30) PRIMARY KEY,
track_name VARCHAR(100),
track_popularity INT,
CONSTRAINT fk_tracks_trackfeatures FOREIGN KEY (id) REFERENCES track_features(track_id)
);

CREATE TABLE albums_artists(
album_id VARCHAR(30), artist_id VARCHAR(30),
CONSTRAINT pk_albums_artists PRIMARY KEY (album_id, artist_id),
CONSTRAINT fk_albums_artists_albums FOREIGN KEY (album_id) REFERENCES albums(id),
CONSTRAINT fk_albums_artists_artists FOREIGN KEY (artist_id) REFERENCES artists(id)
);

CREATE TABLE albums_tracks(
track_id VARCHAR(30), album_id VARCHAR(30),
CONSTRAINT pk_albums_tracks PRIMARY KEY (album_id,track_id),
CONSTRAINT fk_albums_tracks_albums FOREIGN KEY (album_id) REFERENCES albums(id),
CONSTRAINT fk_albums_tracks_tracks FOREIGN KEY (track_id) REFERENCES tracks(id)
);

CREATE TABLE tracks_artists(
track_id VARCHAR(30), artist_id VARCHAR(30),
CONSTRAINT pk_tracks_artists PRIMARY KEY (track_id, artist_id),
CONSTRAINT fk_tracks_artists_tracks FOREIGN KEY (track_id) REFERENCES tracks(id),
CONSTRAINT fk_tracks_artists_artists FOREIGN KEY (artist_id) REFERENCES artists(id)
);