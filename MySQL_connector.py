import mysql.connector
from mysql.connector import errorcode
import warnings
import pandas as pd


class MYSQL_connector:
    def __init__(self, user, password, host, database):
        self.user = user
        self.password = password
        self.host = host
        self.database = database
        self.cnx = None

        self.check_connector()

    def open_connection(self):
        self.cnx = mysql.connector.connect(user=self.user,
                                           password=self.password,
                                           host=self.host,
                                           database=self.database)

    def close_connection(self):
        self.cnx.commit()
        self.cnx.close()

    def check_connector(self):
        try:
            self.open_connection()
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your username or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
        finally:
            if self.cnx != None:
                print("Connection successfully established.")
                self.cnx.close()

    def execute_query(self, query):

        self.open_connection()

        if query.endswith('.txt'):
            with open(query) as f:
                sql_file = f.read()

            ## if below doesn't work ##
            # mycursor = self.cnx.cursor()
            # mycursor.execute(sql_file, multi=True)

            for statement in sql_file.split(';'):
                mycursor = self.cnx.cursor()
                mycursor.execute(statement)

            if sql_file.strip().lower().startswith("select"):
                return mycursor.fetchall()

        else:
            mycursor = self.cnx.cursor()
            mycursor.execute(query)

        try:
            return mycursor.fetchall()
        except mysql.connector.errors.InterfaceError:
            return

    def insert(self, table, values):

        query = f'INSERT INTO {table} VALUES {values};'

        self.open_connection()
        mycursor = self.cnx.cursor()

        try:
            mycursor.execute(query)
        except mysql.connector.Error as err:
            if not err.msg.startswith('Duplicate entry'):
                print(err.msg)
        finally:
            self.close_connection()

    def select(self, table, column, where=None):

        if where != None:
            query = f'SELECT {column} FROM {table} WHERE {where};'
        else:
            query = f'SELECT {column} FROM {table};'

        self.open_connection()
        mycursor = self.cnx.cursor()

        try:
            mycursor.execute(query)
            ret = mycursor.fetchall()

        except mysql.connector.Error as err:
            print(err.msg)
        finally:
            self.close_connection()
            return ret

    def delete_table(self, table):

        self.open_connection()
        mycursor = self.cnx.cursor()

        try:
            mycursor.execute('SET SQL_SAFE_UPDATES = 0;')
            mycursor.execute(f'DELETE FROM {table}')
            mycursor.execute('SET SQL_SAFE_UPDATES = 1;')
        except mysql.connector.Error as err:
            print(err.msg)
        finally:
            self.close_connection()

    def create_pandas_df(self, query_file):
        if query_file.endswith('.txt'):
            with open(query_file) as f:
                sql_file = f.read()
        self.open_connection()

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result_dataFrame = pd.read_sql(sql_file, self.cnx)

        return result_dataFrame