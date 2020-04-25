from cs50 import SQL
from flask import Flask, request, render_template, redirect, url_for, flash, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import login_required

# Configure application
app = Flask(__name__)

# Configure session to use filesystem
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
Session(app)

# Configure cs50 library to use SQLite database
db = SQL("sqlite:///messages.db")


@app.route("/", methods=["GET", "POST"])
def index():

    # User reached route via POST (as by submitting form)
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        # Ensure username was submitted
        if not username:
            flash("Please provide a username", "danger")
            return redirect("/")

        # Ensure password was submitted
        if not password:
            flash("Password was left blank", "danger")
            return render_template("index.html")

        # Query database for username
        users = db.execute("SELECT * FROM users WHERE username = :username", username=username)

        # Ensure username exists and password is correct
        if len(users) != 1 or not check_password_hash(users[0]["hash"], password):
            flash("Username / Password incorrect", "warning")
            return redirect("/chat")

        # Remember which user has logged in
        session["user_id"] = users[0]["id"]

        # Load chatbox
        messages = db.execute("SELECT * FROM messages ORDER BY ts DESC")
        return render_template("chat.html", messages=messages, user_id=session["user_id"])

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("index.html")


@app.route("/chat", methods=["GET", "POST"])
@login_required
def chat():

    # User reached route via POST (as by submitting form)
    if request.method == "POST":

        # Returns a datetime object containing the local date and time
        dateTimeObj = datetime.now()


        # Update database
        message = request.form.get("message")
        user_id = int(session["user_id"])
        if message:
            db.execute("INSERT INTO messages (message, type, ts, user_id) VALUES (:message, 'text', :ts, :user_id)", message=message, ts=dateTimeObj, user_id=user_id)


        # Render template passing in messages
        messages = db.execute("SELECT * FROM messages ORDER BY ts DESC")
        return render_template("chat.html", messages=messages, user_id=user_id)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        messages = db.execute("SELECT * FROM messages ORDER BY ts DESC")
        return render_template("chat.html", messages=messages, user_id=session["user_id"])

@app.route("/register", methods=["GET", "POST"])
def register():

    # User reached route via POST (as by submitting form)
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        users = db.execute("SELECT * FROM users WHERE username = :username", username=username)

        # Username does not exist
        if len(users) != 1:

            # Update database
            db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)", username=username, hash=generate_password_hash(request.form.get("password")))
            return redirect("/")

        # Usename already taken
        else:
            flash("Username already taken", "warning")
            return redirect("/register")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")