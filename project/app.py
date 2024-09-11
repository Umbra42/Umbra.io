import os
import platform
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from celery.result import AsyncResult
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, is_admin
from celery_config import make_celery
from upload import make_folder, get_paths

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SYSTEM"] = platform.system()
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'files')
app.config['DEBUG'] = True
app.config['broker_url'] = 'amqp://localhost//'
app.config['result_backend'] = 'rpc://'

Session(app)
db = SQL("sqlite:///project.db")
print(" > calling make_celery")
celery = make_celery(app)
    
import tasks

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
    print(" > /upload called")
    system = app.config['SYSTEM']
    upload_files = request.files.getlist('files')
    N_upload_files = len(upload_files)
    upload_folder = app.config['UPLOAD_FOLDER']
    
    print(type(upload_folder))
    if not upload_folder:
        print(" > calling make_folder")
        make_folder(upload_folder)

    if N_upload_files <= 0:
        return jsonify({"error": "File upload failed"}), 400

    print(" > making filepaths for temp upload.\ncalling get_paths")
    file_paths = get_paths(upload_files, upload_folder) 
    print(f"returned filepaths:{file_paths}")
    
    print(f"> calling start_upload with: \n{N_upload_files}, \n{upload_folder}, \n{file_paths}, \n{system}")
    task = tasks.start_upload.apply_async(
        args=[N_upload_files, upload_folder, file_paths, system]
        )
    app.logger.info(f"Task ID: {task.id} - Status: {task.status}")
    
    print("task : ", task)
    session['task_id'] = task.id
    return jsonify({'task_id': task.id}, 202)
        
@app.route("/status/<task_id>")
def task_status(task_id):
    task = AsyncResult(task_id, app=celery)
    
    if task.state == 'PENDING':
        print(type(task), task.state)
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
        print(response)    

    elif task.state != 'FAILURE':
        print(type(task), task.state)
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        print(response)    
          
    else:
        print(type(task), task.state)
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': str(task.info), 
        }
        print(response)  

    return jsonify(status=task.state)


if __name__ == '__main__':
    app.run(debug=True)
