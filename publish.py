import argparse
import os
import pickle
from datetime import date

import numpy as np
from sklearn.preprocessing import StandardScaler

from handlers.mqtt.mqtt_handler import MQTT_handler
from handlers.music.spotify_handler import SpotifyHandler
from handlers.mysql.mysql_connector import MYSQL_connector


def preprocess_data(df):
    x = df.drop(columns=['artist_name', 'track_name', 'track_popularity', 'release_date'])
    sc = StandardScaler()
    sc.fit_transform(x)

    return sc.transform(x)


def get_trending(sp_handler):
    artists = list()
    tracks = list()

    top50today = 'https://open.spotify.com/playlist/37i9dQZEVXbIQnj7RRhdSX'
    top50 = sp_handler.get_playlist_tracks(top50today)

    for item in top50:
        artists.append(item['artists'])
        tracks.append(item['track_name'])

    return artists, tracks


def make_predictions(df, songs, artists):
    x = preprocess_data(df)

    global preds1, preds2

    for model_name in os.listdir('models'):
        with open(os.path.join('models', model_name), 'rb') as file:
            model = pickle.load(file)

        preds1 = model.predict(x)
        preds2 = model.predict(x)

    payload = {"last_update": date.today().isoformat(),
               "trending_songs": list()}

    for i in range(len(songs)):

        if type(artists[i]) == list:
            artists[i] = ' & '.join(artists[i])

        cur_song = songs[i]
        cur_artist = artists[i]
        cur_popularity = df[df.track_name == songs[i]].track_popularity.tolist()

        try:
            cur_popularity = int(cur_popularity[0])
        except IndexError:
            cur_popularity = 'ND'

        payload["trending_songs"].append(
            {
                "track_name": cur_song,
                "artist_name": cur_artist,
                "current_popularity": cur_popularity,
                "in_6_months": np.round(preds1[i]),
                "in_12_months": np.round(preds2[i])
            }
        )

    return payload


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        description="Make and public predictions with songs information from MySQL database.")
    arg_parser.add_argument("--mysql_db", type=str, required=True, default=None, help="The MySQL database")
    arg_parser.add_argument("--mysql_host", type=str, required=True, default=None, help="The MySQL host")
    arg_parser.add_argument("--mysql_user", type=str, required=True, default=None, help="The MySQL username")
    arg_parser.add_argument("--mysql_password", type=str, required=True, default=None, help="The MySQL password")

    args = arg_parser.parse_args()

    sql = MYSQL_connector(host=args.mysql_host,
                          user=args.mysql_user,
                          password=args.mysql_password,
                          database=args.mysql_db)

    spt = SpotifyHandler()

    new_artists, new_songs = get_trending(spt)

    features_df = sql.create_pandas_df('sql_queries/extract_info.sql')

    features_df = features_df.loc[features_df['track_name'].isin(new_songs)]
    features_df = features_df.sort_values(by='track_popularity')
    features_df.drop_duplicates(subset='track_name')

    predictions = make_predictions(features_df, new_songs, new_artists)

    mqtt_handler = MQTT_handler()

    mqtt_handler.publish(str(predictions), 'song-popularity/predictions')
