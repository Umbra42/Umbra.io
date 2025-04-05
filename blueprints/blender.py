import extensions 
from flask import Blueprint, jsonify, current_app
from Blender import check_install_blender, is_running, run_listener
from tasks import init_blender
from Upload import blender_progress
blender_bp = Blueprint('blender', __name__)

@blender_bp.route("/check", methods=["GET"])
def check_blender():
    blender_progress(status="Checking Blender Installation called")
    blender_path = check_install_blender(current_app)
    return jsonify({"blender": blender_path})
    
@blender_bp.route("/start", methods=["POST"])
def start_blender_listener():
    blender_progress(status="Starting Blender Listener")
    if not current_app.config["BLENDER_PATH"]:
        current_app.config["BLENDER_PATH"] = init_blender(current_app)
    
    process = extensions.WATCHER_PROCESS

    if not is_running(process):
        return run_listener()
    else:
        blender_progress(status="Blender Listener already running")
        return jsonify({"status": "running", "message": "Blender Listener already running"})
        
@blender_bp.route("/stop", methods=["POST"])
def stop_blender_listener():
    blender_progress(status="Stopping Blender Listener")
    process = extensions.WATCHER_PROCESS
    if is_running(process):
        process.terminate()
        process.wait()
        process = None
        blender_progress(status="Blender Listener stopped")
        return jsonify({"status": "stopped", "message": "Blender Listener Stopped"})
    return jsonify({"status": "not runnig", "message": "Blender Listener not running"})
