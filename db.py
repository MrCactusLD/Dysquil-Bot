import os
import sqlite3
from sqlite3 import Error
from time import sleep

path = 'db'
db = '/bots.db'
database = os.path.join(os.getcwd(), path) + db

def create_connection(db_file):
    """ create a database connection to a SQLite database """

    conn = None

    try: 
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

def setup_table(conn):
    sql_default_bot_table= """CREATE TABLE IF NOT EXISTS Bot(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name text NOT NULL,
    token text NOT NULL,
    app_id INTEGER NOT NULL)"""
    
    execute(conn,sql_default_bot_table)

def execute(conn, line):
    try:
            c = conn.cursor()
            c.execute(line)
            return True
    except Error as e:
        print(e)
        return False

def delete_bot(id):
    conn = create_connection(os.path.join(os.getcwd(), path) + db)
    try: 
        c = conn.cursor()  
        c.execute("""
        DELETE FROM Bot
        WHERE id = """+ str(id) +""";""")
        conn.commit()
        conn.close()
    except Error as e:
        print(e)

def add_bot(name,token,app_id):
    conn = create_connection(os.path.join(os.getcwd(), path) + db)
    try: 
        c = conn.cursor()  
        c.execute("""INSERT INTO Bot(name,token,app_id) VALUES(\""""+ str(name) +"""\",\""""+ str(token) +"""\",\""""+ str(app_id) +"""\")""")
        conn.commit()
        conn.close()
    except Error as e:
        print(e)
        
def get_bots_full():
    conn = create_connection(os.path.join(os.getcwd(), path) + db)
    try: 
        c = conn.cursor()
        c.execute("""SELECT * FROM Bot""")
        s = c.fetchall()
        conn.close()
        return s
    except Error as e:
        print(e)

def get_bots_names():
    conn = create_connection(os.path.join(os.getcwd(), path) + db)
    try: 
        c = conn.cursor()
        c.execute("""SELECT id,name FROM Bot""")
        s = c.fetchall()
        conn.close()
        return s
    except Error as e:
        print(e)


