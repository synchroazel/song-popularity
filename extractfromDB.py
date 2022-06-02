from MySQL_connector import MYSQL_connector
from pprint import pprint
import pandas as pd
import sqlalchemy


def get_data(connectionSQL, query_file):
    output = connectionSQL.execute_query(query_file)
    return output


conn = MYSQL_connector(user = 'root', password="",
                       host = "127.0.0.1", database = "song_popularity")



print(conn.create_pandas_df("extract_info.txt"))









