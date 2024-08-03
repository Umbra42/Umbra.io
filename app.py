import os
import platform
import threading

from celery import Celery 
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import make_celery, apology, login_required, is_admin, init, start_upload, progress

# Configure application
app = Flask(__name__)
app.config.update(
    CELERY_BROKER_URL='pyamqp://guest@localhost//',
    CELERY_RESULT_BACKEND='db+sqlite:///results.sqlite'
)
# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SYSTEM"] = platform.system()
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'files')
app.config['DEBUG'] = True

Session(app)
db = SQL("sqlite:///project.db")
celery = make_celery(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    if session.get("user_id"):
        logout()
    return render_template("layout.html", page = "about-me")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    return render_template("layout.html", page = "contact")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            return apology("must provide username", 403)
        elif not password:
            return apology("must provide password", 403)

        # Query database for username
        users = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Ensure username exists and password is correct
        if len(users) != 1 or not check_password_hash(users[0]["hash"], password):
            return redirect("/register")

        id = users[0]["id"]
        # Remember which user has logged in
        session["user_id"] = id
        session["user_name"] = username
        session["is_admin"] = is_admin(id)
        # Redirect user to home page
        return redirect("/BASE")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("layout.html", page = "login")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if not username or len(rows) != 0:
            return apology("username must be submitted and be unique", 400)

        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not password or not confirmation or password != confirmation:
            return apology("passwords do not match", 400)

        passhash = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, passhash)
        flash("registation succesful please log in")
        return redirect("/login")
    else:
        return render_template("layout.html", page = "register")

@app.route("/BASE")
@login_required
def BASE():
    return render_template("layout.html", page = "BASE")


@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")

@app.route("/upload", methods=["POST"])
@login_required
def upload():
    if request.method == 'POST':
        upload_folder = app.config['UPLOAD_FOLDER']
        init(upload_folder)
    
        upload_files = request.files.getlist('files')
        N_upload_files = len(upload_files)
        if N_upload_files <= 0:
            return apology("no files selected", 400)
    
        task = start_upload.apply_async(args=[N_upload_files, upload_files, upload_folder, app])
        session['task_id'] = task.id
        return jsonify({'task_id': task.id}, 202)
        
    return redirect("/BASE")

@app.route("/upload-progress/<task_id>")
def upload_progress(task_id):
    return progress(task_id)

if __name__ == '__main__':
    app.run(debug=True)
