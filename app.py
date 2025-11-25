import logging
from flask import Flask, request, render_template, redirect, session
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", os.urandom(24))

logging.basicConfig(filename="app.log", level=logging.INFO)


def get_db():
    return sqlite3.connect("secure.db")

@app.route('/')
def index():
    return render_template("index.html")

#secure login
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method =='POST':
        username = request.form["username"]
        password = request.form["password"]

        #Secure is parameterised query
        db = get_db()
        user = db.execute("SELECT password FROM users WHERE username=?",(username,)).fetchone()


        if user and check_password_hash(user[0], password):
            session["user"] = username
            logging.info(f"User logged in: {username}")
            return redirect("/notes")
        
        logging.warning(f"Failed login attempt for {username}")
        return "Invalid credentials"
    
    return render_template("login.html")

#secure registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]

        hashed = generate_password_hash(password)

        db = get_db()
        db.execute("INSERT INTO users (username, password)VALUES (?,?)", (username, hashed))
        db.commit()

        logging.info(f"New user registered: {username}")

        return redirect("/login")
    return render_template("register.html")

#secure notes stored in XSS
@app.route('/notes', methods=['GET','POST'])
def notes():
    if "user" not in session:
        return redirect("/login")
    db = get_db()

    if request.method =='POST':
        note = request.form["note"]

        db.execute("INSERT INTO notes (username, note) VALUES(?,?)", (session["user"], note))
        db.commit()
        logging.info(f"Note added for user: {session['user']}")

    notes = db.execute("SELECT note FROM notes WHERE username=?",(session["user"],)).fetchall()

    return render_template("notes.html", notes=notes)

# fixed reflected XSS
@app.route('/search')
def search():
    q = request.args.get("q","")

    #safe rendering
    return render_template("search.html", q=q)

if __name__=="__main__":
    app.run(debug=True)


