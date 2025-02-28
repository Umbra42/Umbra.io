import os
import platform
import logging
from flask import Flask
from flask_session import Session
from flask_cors import CORS
from extensions import socketio
from tasks import init_blender
from Upload import make_folder


def register_blueprints(app):
    from blueprints.auth import auth_bp
    from blueprints.main import main_bp
    from blueprints.upload import upload_bp
    from blueprints.blender import blender_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(main_bp, url_prefix="/")
    app.register_blueprint(upload_bp, url_prefix="/upload")
    app.register_blueprint(blender_bp, url_prefix="/blender")


def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5000"}})
    
    logging.getLogger("watchdog").setLevel(logging.WARNING)
    logging.basicConfig(level=logging.INFO)

    app.config["SECRET_KEY"] = ""
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["UPLOAD_FOLDER"] = make_folder(os.path.join(os.getcwd(), 'files'))
    app.config["SYSTEM"] = platform.system()
    app.config["APPS_PATH"] = make_folder(os.path.join(os.getcwd(), 'apps'))
    app.config["BLENDER_PATH"] = init_blender(app)
    Session(app)
    register_blueprints(app)
    socketio.init_app(app)
        
    return app


if __name__ == '__main__':
    app = create_app()
    socketio.run(
        app, 
        host="0.0.0.0", 
        port=5000, 
        debug=True, 
        use_reloader=True
    )
