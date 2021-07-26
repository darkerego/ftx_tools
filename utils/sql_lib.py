import os
import sys
import sqlite3

class SQLLiteConnection:
    def __init__(self):
        self.dbName = os.path.dirname(os.path.abspath(sys.argv[0])) + "/ftxdb.sqlite"
        print(f'Connecting to  {self.dbName}')
        conn = sqlite3.connect(self.dbName)
        # check DB
        curs = conn.cursor()
        curs.execute("""create table if not exists orders ('values' TEXT)""")
        conn.commit()
        curs = conn.cursor()
        curs.execute("""create table if not exists signals ('values' TEXT)""")
        conn.commit()

        conn.commit()
        conn.close()


    def search(self, value, table='signals'):
        conn = sqlite3.connect(self.dbName)
        curs = conn.cursor()
        value = str(value)
        curs.execute(f"SELECT * FROM {table} WHERE (?)", (value,))
        conn.commit()
        conn.close()

    def append(self, value, table='signals'):
        conn = sqlite3.connect(self.dbName)
        curs = conn.cursor()
        value = str(value)
        curs.execute(f"INSERT INTO {table} VALUES(?)", (value, ))
        conn.commit()
        conn.close()

    def get_list(self, table='signals'):
        conn = sqlite3.connect(self.dbName)
        curs = conn.cursor()
        curs.execute(f"SELECT * from {table}" )
        rows = curs.fetchall()
        res = []
        for row in rows:
            res.append(row[0])
        conn.commit()
        conn.close()
        return res

    def remove(self, item, table='signals'):
        conn = sqlite3.connect(self.dbName)
        curs = conn.cursor()
        item = str(item)

        curs.execute(f"delete from  {table} where `values`=?", (item, ))
        conn.commit()
        conn.close()

    def clear(self, table='signals'):
        conn = sqlite3.connect(self.dbName)
        curs = conn.cursor()
        curs.execute(f"delete * from {table}")
        conn.commit()
        conn.close()

    def disconnect(self):
        self.disconnect()
