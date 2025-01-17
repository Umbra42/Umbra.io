from flask import Blueprint, render_template, session
from helpers import login_required
from .auth import logout

main_bp = Blueprint('main', __name__)

@main_bp.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@main_bp.route("/")
def index():
    if session.get("user_id"):
        logout()
    return render_template("layout.html", page="about-me")

@main_bp.route("/contact", methods=["GET", "POST"])
def contact():
    return render_template("layout.html", page="contact")

@main_bp.route("/BASE")
@login_required
def base():
    return render_template("layout.html", page="BASE")