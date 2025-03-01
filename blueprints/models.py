import os
from flask import send_from_directory, Blueprint, current_app, request, jsonify


models_bp = Blueprint('models', __name__)

@models_bp.route("/display", methods=["POST"])
def display():
    file = request.json.get("file")
    if not file:
        return jsonify({"error": "file not provided"}), 400
    
    return send_from_directory(current_app.config["DISPLAY_FOLDER"], file)