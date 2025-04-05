import os
import subprocess
import extensions 
from flask import Blueprint, json, jsonify, request, current_app
from Blender import check_install_blender, is_running
from tasks import init_blender
from Upload import update_progress
blender_bp = Blueprint('blender', __name__)

@blender_bp.route("/check", methods=["GET"])
def check_blender():
    update_progress(status="Checking Blender Installation called")
    blender_path = check_install_blender(current_app)
    return jsonify({"blender": blender_path})
    
@blender_bp.route("/start", methods=["POST"])
def start_blender_listener():
    update_progress(status="Starting Blender Listener")
    if not current_app.config["BLENDER_PATH"]:
        current_app.config["BLENDER_PATH"] = init_blender(current_app)
    
    process = extensions.WATCHER_PROCESS
    if not is_running(process):
        run_listener()
        data = request.get_json()
        task_id = data.get("task_id")
        process_folder = current_app.config["PROCESS_FOLDER"]
        glb_folder = current_app.config["MODELS_FOLDER"]
        progress = json.dumps(extensions.UPLOAD_PROGRESS_TRACKER.get(task_id, {}))
        try:
            update_progress(status="Passing data to and starting Blender Listener script")
            blender = current_app.config["BLENDER_PATH"]
            script = os.path.join(os.getcwd(), 'scripts', 'blender_listener.py')
            extensions.WATCHER_PROCESS = subprocess.Popen([
                    blender, 
                    "--background", 
                    "--python", 
                    script, 
                    "--",
                    process_folder,
                    glb_folder, 
                    task_id,
                    progress
                ])
            return jsonify({"status": "started", "message": "Blender Listener Started"})
        except Exception as e:
            update_progress(status="Failed to start Blender Listener")
            return jsonify({"status": "error", "message": str(e)},500)
    else:
        update_progress(status="Blender Listener already running")
        return jsonify({"status": "running", "message": "Blender Listener already running"})
        
@blender_bp.route("/stop", methods=["POST"])
def stop_blender_listener():
    update_progress(status="Stopping Blender Listener")
    process = extensions.WATCHER_PROCESS
    if is_running(process):
        process.terminate()
        process.wait()
        process = None
        update_progress(status="Blender Listener stopped")
        return jsonify({"status": "stopped", "message": "Blender Listener Stopped"})
    return jsonify({"status": "not runnig", "message": "Blender Listener not running"})
