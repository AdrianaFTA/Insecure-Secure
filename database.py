import sqlite3

db = sqlite3.connect("secure.db")

# Users table – password stored as BLOB because bcrypt hash is bytes
db.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password BLOB
)
""")

# Notes table
db.execute("""
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    note TEXT
)
""")

db.commit()
db.close()

print("Secure database created successfully.")