import warnings

import mysql.connector
import pandas as pd
from mysql.connector import errorcode


class MYSQL_connector:
    """
    Includes a set of methods to interact with a MySQL instance
    """

    def __init__(self, user, password, host, database):
        self.user = user
        self.password = password
        self.host = host
        self.database = database
        self.cnx = None

        self.check_connector()

    def open_connection(self):
        """
        Opens a connection to a running MySQL instance and to a given database.
        """

        self.cnx = mysql.connector.connect(user=self.user,
                                           password=self.password,
                                           host=self.host,
                                           database=self.database)

    def close_connection(self):
        """
        Closes a previously opened connection.
        """

        self.cnx.commit()
        self.cnx.close()

    def check_connector(self):
        """
        Checks if connection was successful. If not, shows the error message.
        """

        try:
            self.open_connection()
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("[ERROR] Something is wrong with your username or password. Please Try again.")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print(f"[ERROR] Database {self.database} does not exist")
            else:
                print(err)
        finally:
            if self.cnx != None:
                print(f"[INFO] Connection successfully established with {self.database}.")
                self.cnx.close()

    def execute_query(self, query):
        """
        Executes a query given either a statement as a <str> or a .sql file with multiple statements.
        """

        self.open_connection()

        if query.endswith('.sql'):
            with open(query) as f:
                sql_file = f.read()

            ret = list()
            for statement in sql_file.split(';'):
                mycursor = self.cnx.cursor()
                mycursor.execute(statement)
                try:
                    ret.extend(mycursor.fetchall())
                except mysql.connector.errors.InterfaceError:
                    pass
            return ret if len(ret) != 0 else None

        else:
            mycursor = self.cnx.cursor()
            mycursor.execute(query)
            try:
                return mycursor.fetchall()
            except mysql.connector.errors.InterfaceError:
                return

    def insert(self, table, values):
        """
        Performs a `INSERT INTO table VALUES values` query.
        """

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

    def select(self, table, column, cond=None):
        """
        Performs a `SELECT column FROM table` query, with an optional `WHERE cond` parameter.
        """

        if cond != None:
            query = f'SELECT {column} FROM {table} WHERE {cond};'
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
        """
        Performs a `DELETE FROM table` query.
        """

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
        """
        Given a .sql file returns a pandas DataFrame with the resulting table.
        """

        if query_file.endswith('.sql'):
            with open(query_file) as f:
                sql_file = f.read()
        self.open_connection()

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result_dataFrame = pd.read_sql(sql_file, self.cnx)

        return result_dataFrame
