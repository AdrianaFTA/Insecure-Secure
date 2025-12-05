import bcrypt
import logging
from flask import Flask, request, render_template, redirect, session
import sqlite3
import os
from dotenv import load_dotenv



load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback_secret_key")




# Logging

logging.basicConfig(
    filename='secure.log',
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s"
)


# Database helper

def get_db():
    return sqlite3.connect("secure.db", check_same_thread=False)

# Index page

@app.route('/')
def index():
    logout_msg = request.args.get("logout")
    return render_template("index.html", logout_msg=logout_msg)


# Secure Login

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        user = db.execute(
            "SELECT username, password FROM users WHERE username=?",
            (username,)
        ).fetchone()

        if user and bcrypt.checkpw(password.encode(), user[1]):
            session["user"] = username
            logging.info(f"LOGIN SUCCESS: {username}")
            return redirect("/notes")

        logging.warning(f"LOGIN FAILED: {username}")
        return "Invalid Login"

    return render_template("login.html")

# --------------------------
# Secure Registration
# --------------------------
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]

        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        db = get_db()
        db.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed_pw)
        )
        db.commit()

        logging.info(f"NEW USER REGISTERED: {username}")
        return redirect("/login")

    return render_template("register.html")

# --------------------------
# Secure Notes (Create + Read)
# --------------------------
@app.route('/notes', methods=['GET','POST'])
def notes():
    if "user" not in session:
        return redirect("/login")

    db = get_db()

    if request.method == 'POST':
        note = request.form["note"]
        db.execute(
            "INSERT INTO notes (username, note) VALUES (?, ?)",
            (session["user"], note)
        )
        db.commit()

        logging.info(f"NOTE CREATED by {session['user']}: {note}")

    notes = db.execute(
        "SELECT id, note FROM notes WHERE username=?",
        (session["user"],)
    ).fetchall()

    undo_available = request.args.get("undo_available")

    return render_template("notes.html", notes=notes, undo_available=undo_available)

# --------------------------
# Edit Note
# --------------------------
@app.route('/edit/<int:note_id>', methods=['GET','POST'])
def edit(note_id):
    if "user" not in session:
        return redirect("/login")

    db = get_db()

    if request.method == "POST":
        updated_note = request.form["note"]
        db.execute(
            "UPDATE notes SET note=? WHERE id=? AND username=?",
            (updated_note, note_id, session["user"])
        )
        db.commit()

        logging.info(f"NOTE UPDATED by {session['user']} (ID {note_id}): {updated_note}")
        return redirect("/notes")

    row = db.execute(
        "SELECT note FROM notes WHERE id=? AND username=?",
        (note_id, session["user"])
    ).fetchone()

    if row is None:
        return "Note not found"

    return render_template("edit.html", note=row[0], note_id=note_id)

# --------------------------
# Delete Note + Undo
# --------------------------
@app.route('/delete/<int:note_id>')
def delete(note_id):
    if "user" not in session:
        return redirect("/login")

    db = get_db()

    row = db.execute(
        "SELECT id, username, note FROM notes WHERE id=? AND username=?",
        (note_id, session["user"])
    ).fetchone()

    if row is None:
        return redirect("/notes")

    # Store note temporarily for undo
    session["deleted_note"] = {
        "username": row[1],
        "note": row[2]
    }

    db.execute("DELETE FROM notes WHERE id=?", (note_id,))
    db.commit()

    logging.info(f"NOTE DELETED by {session['user']} (ID {note_id})")

    return redirect("/notes?undo_available=1")

@app.route('/undo')
def undo_delete():
    if "user" not in session:
        return redirect("/login")

    deleted = session.get("deleted_note")

    if not deleted:
        return redirect("/notes")

    db = get_db()
    db.execute(
        "INSERT INTO notes (username, note) VALUES (?, ?)",
        (deleted["username"], deleted["note"])
    )
    db.commit()

    session.pop("deleted_note", None)

    logging.info(f"NOTE RESTORED for {session['user']}")

    return redirect("/notes")

# --------------------------
# Secure Search
# --------------------------
@app.route('/search')
def search():
    if "user" not in session:
        return redirect("/login")

    q = request.args.get("q", "")

    db = get_db()
    results = db.execute(
        "SELECT id, note FROM notes WHERE username=? AND note LIKE ?",
        (session["user"], f"%{q}%")
    ).fetchall()

    return render_template("search.html", q=q, results=results)

# --------------------------
# Logout
# --------------------------
@app.route('/logout')
def logout():
    user = session.get("user")
    session.clear()

    logging.info(f"LOGOUT: {user}")
    return redirect("/?logout=1")

# --------------------------
# Run App
# --------------------------
if __name__ == "__main__":
    app.run(debug=True)