import argparse
from datetime import date
import os
import pickle
from pprint import pprint
from sklearn.preprocessing import StandardScaler

from handlers.music.spotify_handler import SpotifyHandler
from handlers.mysql.mysql_connector import MYSQL_connector
from handlers.mqtt.mqtt_handler import MQTT_handler


def preprocess_data(df):
    df.track_popularity = df.track_popularity / 100

    y = df.track_popularity
    x = df.drop(columns=['artist_name', 'track_name', 'track_popularity', 'release_date'])

    sc = StandardScaler()
    sc.fit_transform(x)

    x = sc.transform(x)

    print(f'[INFO] Info on {df.shape[0]} tracks imported and preprocessed.')

    return x, y


def trending_songs(sp_handler):
    top50today = 'https://open.spotify.com/playlist/37i9dQZEVXbIQnj7RRhdSX'
    new_songs = list()
    new_artists = list()

    for item in sp_handler.get_playlist_tracks(top50today):
        new_songs.append(item['track_name'])
        new_artists.append(item['artists'])

    return new_songs, new_artists


def make_predictions(df, new_songs, new_artists):
    df = df.loc[df['track_name'].isin(new_songs)].copy()

    x, y = preprocess_data(df)

    for model_name in os.listdir('models'):
        with open(os.path.join('models', model_name), 'rb') as file:
            model = pickle.load(file)

        model1_preds = model.predict(x)
        model2_preds = model.predict(x)
        actual = y.tolist()

    payload = {'last_update': date.today().isoformat(),
               'trending_songs': list()}

    for i in range(len(new_songs)):

        if type(new_artists[i]) == list:
            new_artists[i] = ' & '.join(new_artists[i])

        payload['trending_songs'].append(
            {
                'track_name': new_songs[i],
                'artist_name': new_artists[i],
                'current_popularity': int(actual[i] * 100),
                'in_6_months': int(model1_preds[i] * 100),
                'in_1_2months': int(model2_preds[i] * 100)
            }
        )

    return payload


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

    # new_songs, new_artists = trending_songs(sp_handler)

    new_songs = ['After Hours', 'Fiamme Alte']  # just trying
    new_artists = ['artist 1', 'artist 2']

    df = sql_handler.create_pandas_df('sql_queries/extract_info.sql')

    predictions = make_predictions(df, new_songs, new_artists)

    mqtt_handler = MQTT_handler()

    mqtt_handler.publish(str(predictions), 'song-popularity/predictions')
