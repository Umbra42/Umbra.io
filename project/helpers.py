from cs50 import SQL
from flask import redirect, render_template, session
from functools import wraps


db = SQL("sqlite:///project.db")
                
def notify():
    apology("TODO", 400)

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None and session.get("is_admin") is False:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def is_admin(id):
    query_role = db.execute("SELECT role FROM users WHERE id = ?", id)
    role = query_role[0]
    if role == "admin":
        return True
    else:
        return False
    

