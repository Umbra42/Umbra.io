from cs50 import SQL
db = SQL("sqlite:///project.db")

from flask_socketio import SocketIO
socketio = SocketIO(cors_allowed_origins="*", transports=["websocket", "polling"])

upload_tasks = {}
