import sqlite3


conn = sqlite3.connect('messages.db', isolation_level=None)

message_table = '''CREATE TABLE messages (
    no INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT NOT NULL,
    message TEXT NOT NULL
);'''
  
conn.execute(message_table)

user_table = '''
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    password TEXT NOT NULL
);'''
  
conn.execute(user_table)
