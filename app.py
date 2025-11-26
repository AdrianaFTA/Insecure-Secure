from flask import Flask, request, render_template, redirect, session, url_for
import sqlite3

app = Flask(__name__)
app.secret_key ="123" #hard coded secret, sensitive data exposure

def get_db():
    return sqlite3.connect("insecure.db")

@app.route('/')
def index():
    return render_template("index.html")

#insecure login with plaintext passwords
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]

        #sql injection (vulnerability)
        query = f"SELECT * FROM users WHERE username='{username}'AND password='{password}'"
        user = get_db().execute(query).fetchone()

        if user:
            session["user"] = username
            return redirect("/notes")
        return "Invalid credentials"
    return render_template("login.html")

#insecure registration
@app.route('Insecure-Secure/templates/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]# stored in plaintext

        db = get_db()
        db.execute("INSERT INTO users (username, password) VALUES (?,?)", (username, password))
        db.commit()
        return redirect("/login")
    return render_template("register.html")

#insecure notes stored in XSS
@app.route('/notes', methods=['GET','POST'])
def notes():
    if "user" not in session:
        return redirect("/login")
    
    db = get_db()

    if request.method == 'POST':
        note = request.form["note"]

        #stored XSS saved without sanitisation
        db.execute("INSERT INTO notes (username, note) VALUES (?,?)", (session["user"], note))
        db.commit()

    notes = db.execute("SELECT note FROM notes WHERE username=?", (session["user"],)).fetchall()

    return render_template("notes.html", notes=notes)

# reflected XSS
@app.route('/search')
def search():
    q = request.args.get("q","")

    #output with no sanitisation
    return f"<h1>You searched for : {q}</h1>"

if __name__ == "__main__":
    app.run(debug=True)
    
