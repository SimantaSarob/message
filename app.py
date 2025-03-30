from datetime import timedelta
from sqlalchemy import *
from flask import Flask, flash, redirect, render_template, request, url_for, session
from flask_socketio import SocketIO, send

# database area. DO NOT CHANGE IF YOU DO NOT KNOW WHAT Is HAPPINING HARE!
engine = create_engine('sqlite:///messages.db', connect_args={"check_same_thread": False})
conn = engine.connect()
metadata = MetaData()

messages_table = Table(
    'messages', metadata,
    Column('no', Integer, primary_key=True, autoincrement=True),
    Column('user', String, nullable=False),
    Column('message', String, nullable=False)
)

user_table = Table(
    'user', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String, nullable=False),
    Column('password', String, nullable=False)
)

metadata.create_all(engine)
# database area finishd. 


# Flask application setup
app = Flask(__name__)
app.secret_key = "change it and dont share it. "
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=3)
app.config['SESSION_COOKIE_NAME'] = 'session'
socketio = SocketIO(app)

# Routes
@app.route("/")
def home():
    return render_template("login.html")

@app.route('/login', methods=["POST", "GET"])
def login():
    print(f'\n {request.method} \n')
    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")

        if name and password:
            sqlCheak = select(user_table.c.id).where(user_table.c.name == name, user_table.c.password == password)
            info = conn.execute(sqlCheak).fetchone()
            if info:
                session['name'] = name
                return redirect(url_for("messages"))
        return render_template("login.html")
    else:
        return render_template("login.html")
@app.route('/logout',methods=["POST"])
def logout():
    session.pop('name', None)
    return redirect(url_for("login"))

@app.route('/signup')
def signup():
    return render_template("signup.html")


@app.route('/sign_up', methods=["POST"])
def sign_up():
    name = request.form.get("name")
    password = request.form.get("password")
    if len(name) < 6 or len(name) > 20 or len(password) < 6 or len(password) > 20 or name.isspace():
        return render_template("error.html", error="pass or name is bigger then 20 char or less then 6 char or you didn't do it as I say.", back_url="/signup", back_url_="go back?")
    else:
        sqlFindDuplicateUserName = select(user_table.c.id).where(user_table.c.name == name)
        result = conn.execute(sqlFindDuplicateUserName).fetchone()
        if result:
            return render_template("error.html", error=f"User name {name} is already taken.", back_url="/signup", back_url_="Re-Try?")
        else:
            # Insert new user into the database
            sqlInsertUser = insert(user_table).values(name=name, password=password)
            conn.execute(sqlInsertUser)
            conn.commit()

            # Check if the user was inserted successfully
            sqlCheckUser = select(user_table.c.id).where(user_table.c.name == name, user_table.c.password == password)
            result = conn.execute(sqlCheckUser).fetchone()
            if result:
                session['name'] = name
                return redirect(url_for("login"))
            else:
                return render_template("error.html", error="Failed to create user.", back_url="/signup", back_url_="Re-Try?")

@socketio.on('message')
def handle_message(msg):
    name = session.get('name')
    if not msg.isspace() and msg:
        sqlEnterMessages = insert(messages_table).values(user=name, message=msg)
        conn.execute(sqlEnterMessages)
        conn.commit()
        send({'user': name, 'message': msg}, broadcast=True)

@app.route('/messages', methods=["GET", "POST"])
def messages():
    name_sess = session.get('name')
    sqlGetMessages = select(messages_table.c.user, messages_table.c.message)
    datas = conn.execute(sqlGetMessages).fetchall()

    # Render the messages with the new template
    return render_template("msg.html", messages=datas, name=name_sess)



if __name__ == "__main__":
    socketio.run(app, debug=True, port=5000) # please make it debug = False when you are done with the project.
