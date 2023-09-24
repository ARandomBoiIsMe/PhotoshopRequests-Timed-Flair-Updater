import sqlite3
from sqlite3 import Error

def connect_to_db():
    try:
        connection = sqlite3.connect('visited_posts_data.db')
        connection.execute("""
                    CREATE TABLE IF NOT EXISTS newest_post_time (
                        post_upload_time REAL NOT NULL
                    );
                    """)
        
        return connection
    except Error as e:
        print(e)
        raise

def retrieve_time(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM newest_post_time")
    
    return cursor.fetchone()

def insert_time(connection, creation_time_utc):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM newest_post_time")
    result = cursor.fetchone()

    if result:
        connection.execute("UPDATE newest_post_time SET post_upload_time = ?", (creation_time_utc,))
        connection.commit()

    if not result:
        connection.execute("INSERT INTO newest_post_time (post_upload_time) VALUES (?)", (creation_time_utc,))
        connection.commit()

def close_connection(connection):
    connection.close()