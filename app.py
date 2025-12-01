import bcrypt
from flask import Flask, request, render_template, redirect, session
import sqlite3
import os
from dotenv import load_dotenv

#load enviroment variables
load_dotenv

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback_secret_key")



def get_db():
    return sqlite3.connect("secure.db", check_same_thread=False)

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
        user = db.execute("SELECT username, password FROM users WHERE username=?",
                          (username,)).fetchone()


        if user and bcrypt.checkpw(password.encode(), user[1]):
            session["user"] = username
            return redirect("/notes")
        
        return "Invalid Login"
    
    return render_template("login.html")

#secure registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]

        #hash the password securely

        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        db = get_db()
        db.execute("INSERT INTO users (username, password)VALUES (?,?)", (username, hashed_pw))
        db.commit()

        return redirect("/login")
    return render_template("register.html")

#secure notes, no XSS
@app.route('/notes', methods=['GET','POST'])
def notes():
    if "user" not in session:
        return redirect("/login")
    db = get_db()

    if request.method =='POST':
        note = request.form["note"]

        #stored safley with JINJA ESCAPES
        db.execute("INSERT INTO notes (username, note) VALUES(?,?)", (session["user"], note))
        db.commit()
        

    notes = db.execute("SELECT note FROM notes WHERE username=?",(session["user"],)).fetchall()

    return render_template("notes.html", notes=notes)

#edit note secure 
@app.route("/edit/<int:note_id>", methods=["GET","POST"])
def edit(note_id):
    if "user" not in session:
        return redirect("/login")
    
    db = get_db()

    if request.method == "POST":
        updated_note = request.form["note"]
        db.execute("UPDATE notes SET note=? WHERE id=?",(updated_note, note_id))
        db.commit()
        return redirect("/notes")
    
    row = db.execute("SELECT note FROM notes WHERE id=?", (note_id,)).fetchone()
    if row is None:
        return "Note not found"
    
    return render_template("edit.html", note=row[0])

# delete notes secure 
@app.route("/delete/<int:note_id>")
def delete(note_id):
    if "user" not in session:
        return redirect("/login")
    
    db = get_db()
    db.execute("DELETE FROM notes WHERE id=?", (note_id,))
    
    db.commit()

    return redirect("/notes")

# fixed reflected XSS
@app.route('/search')
def search():
    if "user" not in session:
        return redirect("/login")
    
    q = request.args.get("q","")

    db = get_db()

    #safe sql injection
    results = db.execute(
        "SELECT note FROM notes WHERE username=? AND note LIKE ?",(session["user"], f"%{q}%")).fetchall()
    
    
    return render_template("search.html", q=q, results=results)

#secure logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/?logout=1")


if __name__=="__main__":
    app.run(debug=True)


