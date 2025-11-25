import sqlite3

db = sqlite3.connect("secure.db")
db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
db.execute("CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, username TEXT, note TEXT)")
db.commit()
db.close()