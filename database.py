import sqlite3

conn = sqlite3.connect("insecure.db")
cursor = conn.cursor()

# Users table (plaintext passwords)
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
)
""")

# Notes table (stores XSS)
cursor.execute("""
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    note TEXT
)
""")

conn.commit()
conn.close()

print("Insecure database created.")