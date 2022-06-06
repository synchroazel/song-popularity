import argparse
import os
import pickle
from datetime import date

from sklearn.preprocessing import StandardScaler

from handlers.mqtt.mqtt_handler import MQTT_handler
from handlers.music.spotify_handler import SpotifyHandler
from handlers.mysql.mysql_connector import MYSQL_connector


def get_trending(sp_handler):
    artists = list()
    tracks = list()

    top50today = 'https://open.spotify.com/playlist/37i9dQZEVXbIQnj7RRhdSX'
    top50 = sp_handler.get_playlist_tracks(top50today)

    for item in top50:
        artists.append(item['artists'])
        tracks.append(item['track_name'])

    return tracks, artists


def scale_data(x):
    sc = StandardScaler()
    sc.fit_transform(x)
    return sc.transform(x)


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="Update a MySQL database with songs information.")
    arg_parser.add_argument("--mysql_db", type=str, required=True, default=None, help="The MySQL database")
    arg_parser.add_argument("--mysql_host", type=str, required=True, default=None, help="The MySQL host")
    arg_parser.add_argument("--mysql_user", type=str, required=True, default=None, help="The MySQL username")
    arg_parser.add_argument("--mysql_password", type=str, required=True, default=None, help="The MySQL password")

    args = arg_parser.parse_args()

    sql_handler = MYSQL_connector(host=args.mysql_host,
                                  user=args.mysql_user,
                                  password=args.mysql_password,
                                  database=args.mysql_db)

    sp_handler = SpotifyHandler()

    new_songs, new_artists = get_trending(sp_handler)

    features_df = sql_handler.create_pandas_df('sql_queries/extract_info.sql')
    features_df = features_df.loc[features_df['track_name'].isin(new_songs)]
    features_df = features_df.sort_values(by='track_popularity').drop_duplicates(subset='track_name', keep='first')

    features_df_x = features_df.drop(columns=['artist_name', 'track_name', 'track_popularity', 'release_date'])
    features_df_x = scale_data(features_df_x)

    for model_name in os.listdir('models'):
        with open(os.path.join('models', model_name), 'rb') as file:
            model = pickle.load(file)

        preds1 = model.predict(features_df_x)
        preds2 = model.predict(features_df_x)

    features_df['preds1'] = [int(n * 100) for n in preds1]
    features_df['preds2'] = [int(n * 100) for n in preds2]

    payload = {"last_update": date.today().isoformat(),
               "trending_songs": list()}

    how_many = 10

    for song in new_songs[:how_many]:
        row = features_df.loc[features_df.track_name == song]

        print(row)

        payload['trending_songs'].append(
            {
                "track_name": row.track_name,
                "artist_name": row.artist_name,
                "current_popularity": row.track_popularity,
                "in_6_months": row.preds1,
                "in_12_months": row.preds2
            }
        )

    mqtt_handler = MQTT_handler()

    mqtt_handler.publish(str(payload), 'song-popularity/predictions')
