from MySQL_connector import MYSQL_connector
from pprint import pprint

def get_data(connectionSQL, query_file):
    output = connectionSQL.execute_query(query_file)
    return output


conn = MYSQL_connector(user = 'root', password="volleyball_1199",
                       host = "127.0.0.1", database = "song_popularity")


res = get_data(conn, "query_extractinfo.txt")
pprint(res)





