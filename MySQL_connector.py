import mysql.connector
from mysql.connector import errorcode

class MYSQL_connector:
    def __init__(self, user, password, host, database, cnx = None):
        self.user = user
        self.password = password
        self.host = host,
        self.database = database
        self.cnx = cnx

    def check_connector(self):
        try:
          self.cnx = mysql.connector.connect(user= self.user,
                                        password=self.password,
                                        host=self.host,
                                        database=self.database)
        except mysql.connector.Error as err:
          if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
          elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
          else:
            print(err)
        finally:
            if self.cnx.is_connected():
                print("OK")
                self.cnx.close()

    def create_tables(self, file):
        with open(file) as f:
            lines = f.read()

        mycursor = self.cnx.cursor()

        mycursor.execute(lines)


