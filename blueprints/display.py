import os
from flask import send_from_directory, Blueprint, current_app, request, jsonify

display_bp = Blueprint('display', __name__)

@display_bp.route('/models/<path:filename>')
def get_model(filename):
    return send_from_directory(current_app.config["MODELS_FOLDER"], filename)

@display_bp.route('/code/<path:filename>')
def get_code(filename):
    return send_from_directory(current_app.config["CODE_FOLDER"], filename)

@display_bp.route('/projects/<path:filename>')
def get_project(filename):
    return send_from_directory(current_app.config["PROJECTS_FOLDER"], filename)

def register_socket_events(socketio):
    @socketio.on("Progress_update", namespace="/upload")
    def on_progress(data):
        socketio.emit("progress_update", data, namespace="/upload")

    @socketio.on("request_models")
    def send_models():
        models = [f for f in os.listdir(current_app.config["MODELS_FOLDER"]) if f.endswith(('.glb', '.gltf', '.obj'))]
        socketio.emit("models_list", models)

    @socketio.on("request_code")
    def send_code_snippets():
        code_files = [f for f in os.listdir(current_app.config["CODE_FOLDER"])if f.endswith(('.py', '.js', '.html', '.css', '.sh'))]
        socketio.emit("code_list", code_files)

    @socketio.on("request_projects")
    def send_projects():
        project_files = [f for f in os.listdir(current_app.config["PROJECTS_FOLDER"]) if f.endswith(('.txt', '.md', '.png', '.jpg', '.jpeg', '.mp4'))]
        socketio.emit("projects_list", project_files)