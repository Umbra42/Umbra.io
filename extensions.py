#TODO: import sqlite3 as SQL
from cs50 import SQL
db = SQL("sqlite:///project.db")

from flask_socketio import SocketIO
socketio = SocketIO(cors_allowed_origins="*", async_mode="eventlet")

WATCHER_PROCESS = None
UPLOAD_PROGRESS_TRACKER = {}

