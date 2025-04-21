from flask import Blueprint, jsonify, current_app
from tasks import init_blender, launch_listener, terminat_listener
from Upload import blender_progress

blender_bp = Blueprint('blender', __name__)
   
@blender_bp.route("/start", methods=["POST"])
def start_listener():
    print(" > /blender/start called")
    
    if not current_app.config["BLENDER_PATH"]:
        print(" > /blender/start: Blender path not set")
        current_app.config["BLENDER_PATH"] = init_blender(current_app)
        blender_progress(status="Launching Blender Listener")
        launch_listener()
        return jsonify({"status": "started", "message": "Blender Listener started"})
    else:
        print(" > /blender/start: Blender Listener already running")
        blender_progress(status="Blender Listener already running")
        return jsonify({"status": "running", "message": "Blender Listener already running"})
        
@blender_bp.route("/stop", methods=["POST"])
def stop_listener():
    blender_progress(status="Stopping Blender Listener")
    terminat_listener()
    return jsonify({"status": "stopped", "message": "Blender Listener stopped"})
