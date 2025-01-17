from flask import Blueprint, render_template, request, session, redirect, flash
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, is_admin
from extensions import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
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
            session.clear()
            return render_template("layout.html", page = "register")

        id = users[0]["id"]
        # Remember which user has logged in
        session["user_id"] = id
        session["user_name"] = username
        session["is_admin"] = is_admin(id)
        # Redirect user to home page
        return redirect("/BASE")

    else:
        return render_template("layout.html", page = "login")
    
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
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
    
@auth_bp.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")

@auth_bp.before_request
def check_session():
    if not session.get("user_id") and request.endpoint not in ['auth.login', 'auth.register']:
        return redirect("auth/login")

''' TODO
@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    # Logic for password reset
    pass

@auth_bp.route("/profile", methods=["GET"])
def profile():
    # Render user profile
    pass

@auth_bp.route("/admin", methods=["GET"])
def admin_dashboard():
    if not is_admin(session.get("user_id")):
        return redirect("/auth/login")
    return render_template("admin_dashboard.html")
'''