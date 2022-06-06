import argparse
import pickle
from datetime import date, timedelta

from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

from handlers.mysql.mysql_connector import MYSQL_connector


def preprocess_data(df):
    """
    Returns rescaled features of a given dataframe of song features.
    """

    y = df.track_popularity
    x = df.drop(columns=['artist_name', 'track_name', 'track_popularity', 'release_date'])

    sc = StandardScaler()
    sc.fit_transform(x)

    x = sc.transform(x)

    print(f'[INFO] Info on {df.shape[0]} tracks imported and preprocessed.')

    return x, y


def generate_model(x_train, y_train, filename):
    """
    Generate and train a Ridge regression model with supplied data.
    """

    ridge_regression = Ridge()
    ridge_regression.fit(x_train, y_train)

    pkl_filename = filename
    with open(pkl_filename, 'wb') as f:
        pickle.dump(ridge_regression, f)

    print(f'[INFO] Model {filename} successfully created and saved.')


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="Train models with songs information from MySQL database.")
    arg_parser.add_argument("--mysql_db", type=str, required=True, default=None, help="The MySQL database")
    arg_parser.add_argument("--mysql_host", type=str, required=True, default=None, help="The MySQL host")
    arg_parser.add_argument("--mysql_user", type=str, required=True, default=None, help="The MySQL username")
    arg_parser.add_argument("--mysql_password", type=str, required=True, default=None, help="The MySQL password")

    args = arg_parser.parse_args()

    sql_handler = MYSQL_connector(host=args.mysql_host,
                                  user=args.mysql_user,
                                  password=args.mysql_password,
                                  database=args.mysql_db)

    features_df = sql_handler.create_pandas_df('sql_queries/extract_info.sql')

    today = date.today()

    # Filter songs with release date earlier than 6 and 12 months
    # then rain 2 models to predict 6-months and 12-months popularity

    for months in [6, 12]:

        pastdate = today - timedelta(days=months * 30)

        cur_df = features_df.loc[features_df['release_date'] < pastdate].copy()

        cur_x, cur_y = preprocess_data(cur_df)

        model_name = f'models/model{months}.pickle'

        generate_model(cur_x, cur_y, model_name)

        # save trained models as .pickle
        with open(model_name, 'rb') as file:
            model = pickle.load(file)

        print(f'[INFO] The model has a R-squared value of {model.score(cur_x, cur_y)}')
