import argparse
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.utils import shuffle

from handlers.mysql.mysql_connector import MYSQL_connector


def preprocess_data():
    # scale popularity score to fit in 0-1 interval
    df.track_popularity = df.track_popularity / 100

    shuffle(df)

    df_train, df_test = train_test_split(df, train_size=0.7)

    y_train = df_train.track_popularity
    x_train = df_train.drop(columns=['artist_name', 'track_name', 'track_popularity', 'release_date'])
    y_test = df_test.track_popularity
    x_test = df_test.drop(columns=['artist_name', 'track_name', 'track_popularity', 'release_date'])

    sc = StandardScaler()

    x_train = sc.fit_transform(x_train)
    x_test = sc.transform(x_test)

    return x_train, y_train, x_test, y_test


def generate_model(x_train, y_train):
    ridge_regression = Ridge()
    ridge_regression.fit(x_train, y_train)

    return ridge_regression


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

    x_train, y_train, x_test, y_test = preprocess_data(df)

    model = generate_model(x_train, y_train)
