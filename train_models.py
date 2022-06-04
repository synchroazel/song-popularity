import argparse
import pickle
from datetime import date, timedelta
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

from handlers.mysql.mysql_connector import MYSQL_connector


def preprocess_data(df):
    df.track_popularity = df.track_popularity / 100

    y = df.track_popularity
    x = df.drop(columns=['artist_name', 'track_name', 'track_popularity', 'release_date'])

    sc = StandardScaler()
    sc.fit_transform(x)

    x = sc.transform(x)

    print(f'[INFO] Info on {df.shape[0]} tracks imported and preprocessed.')

    return x, y


def generate_model(x_train, y_train, filename):
    ridge_regression = Ridge()
    ridge_regression.fit(x_train, y_train)

    pkl_filename = filename
    with open(pkl_filename, 'wb') as file:
        pickle.dump(ridge_regression, file)

    print(f'[INFO] Model {filename} successfully created and saved.')


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="Initialize a MySQL database with songs information.")
    arg_parser.add_argument("--mysql_db", type=str, required=True, default=None, help="The MySQL database")
    arg_parser.add_argument("--mysql_host", type=str, required=True, default=None, help="The MySQL host")
    arg_parser.add_argument("--mysql_user", type=str, required=True, default=None, help="The MySQL username")
    arg_parser.add_argument("--mysql_password", type=str, required=True, default=None, help="The MySQL password")

    args = arg_parser.parse_args()

    sql_handler = MYSQL_connector(host=args.mysql_host,
                                  user=args.mysql_user,
                                  password=args.mysql_password,
                                  database=args.mysql_db)

    df = sql_handler.create_pandas_df('sql_queries/extract_info.sql')

    today = date.today()

    for months in [6, 12]:
        pastdate = today - timedelta(days=months * 30)

        cur_df = df.loc[df['release_date'] < pastdate].copy()

        x, y = preprocess_data(cur_df)

        model_name = f'models/model{months}.pickle'

        generate_model(x, y, model_name)

        with open(model_name, 'rb') as file:
            model = pickle.load(file)

        print(f'[INFO] The model has a R-squared value of {model.score(x, y)}')
