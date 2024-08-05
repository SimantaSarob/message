from datetime import timedelta
import sqlite3 , os
from flask import Flask, flash, redirect, render_template, request, url_for, session
from flask_socketio import SocketIO, send

conn = sqlite3.connect('messages.db')
conn = sqlite3.connect('messages.db', check_same_thread=False)

cur = conn.cursor()

# Flask application setup
app = Flask(__name__)
app.secret_key = "change it and dont share it. "
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=3)
app.config['SESSION_COOKIE_NAME'] = 'lungi_man'
socketio = SocketIO(app)

# Routes
@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")

        if name and password:
            cur.execute("SELECT id FROM user WHERE name = ? AND password = ?;", (name, password))
            info = cur.fetchone()
            if info:
                session['name'] = name
                return redirect(url_for("messages"))
        return render_template("login.html")
    else:
        return render_template("login.html")

@app.route('/signup')
def signup():
    return render_template("signup.html")

@app.route('/sign_up', methods=["POST"])
def sign_up():
    name = request.form.get("name")
    password = request.form.get("password")
    print(name,password)
    if len(name) < 6 or len(name) > 20 or len(password) < 6 or len(password) > 20 or name.isspace():
        return render_template("error.html", error="pass or name is bigger then 20 char or less then 6 char or name is just a white space.", back_url="/signup", back_url_="go back?")
    else:
        cur.execute("SELECT id FROM user WHERE name = ? AND password = ?;", (name, password))
        id_ = cur.fetchone()
        if not id_:
            cur.execute("INSERT INTO user (name, password) VALUES (?, ?);", (name, password))
            return redirect(url_for("login"))
        else:
            return render_template("error.html", error=f"User name {name} is not available.", back_url="/signup", back_url_="Re-Try?")

@socketio.on('message')
def handle_message(msg):
    name = session.get('name')
    if not msg.isspace() and msg:
        cur.execute("INSERT INTO messages (user, message) VALUES (?, ?);", (name, msg))
        conn.commit()
        send({'user': name, 'message': msg}, broadcast=True)

@app.route('/messages', methods=["GET", "POST"])
def messages():
    name_sess = session.get('name')

    # Fetch the last 100 messages from the database
    cur.execute("SELECT user, message FROM messages;")
    datas = cur.fetchall()

    # Render the messages with the new template
    return render_template("msg.html", messages=datas, name=name_sess)



if __name__ == "__main__":
    socketio.run(app, debug=True, port=5500)
