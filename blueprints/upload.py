from flask import Blueprint, request, jsonify, session, current_app
from extensions import socketio
from helpers import login_required
from Upload import get_paths
import threading
import uuid
import tasks

upload_bp = Blueprint('upload', __name__)

@upload_bp.route("/upload", methods=["POST"])
@login_required
def upload():
    print(" > /upload called")
    upload_files = request.files.getlist('files')
    if len(upload_files) <= 0:
        return jsonify({"error": "No files uploaded"}), 400
    N_upload_files = len(upload_files)
    upload_folder = current_app.config['UPLOAD_FOLDER']

    print(" > making filepaths for temp upload.\ncalling get_paths")
    file_paths = get_paths(upload_files, upload_folder) 
    print(f"returned filepaths:\n{file_paths}")
    
    try:
        task_id = str(uuid.uuid4())
        print(f"Generated task ID: {task_id}")
    except Exception as e:
        print(f"Failed to generate task_id: {e}")
        return jsonify({"error": "Failed to initialize upload task"}), 500

    upload_progress = {
        "task_id" : task_id,
        "state" : '',
        "overall" : 0,
        "total" : N_upload_files,
        "current" : 0,
        "status" : 'Init upload...'
    }
    upload_progress['status'] = 'initializing task'
    socketio.emit('progress_update', upload_progress)
    
    print(f" > calling start_upload with:\n task_id:{task_id}, \n N_upload_files:{N_upload_files}, \n upload_folder:{upload_folder}, \n file_paths:{file_paths}")
    thread = threading.Thread(target=tasks.start_upload, args=(current_app._get_current_object(), upload_progress, task_id, N_upload_files, upload_folder, file_paths))
    with current_app._get_current_object().app_context():
        upload_progress['state'] = "Running"
        thread.start()
        
    session['task_id'] = task_id
    return jsonify({'status': 'files uploaded successfully', 'task_id': task_id}), 200

''' TODO
@upload_bp.route("/api/progress/<task_id>", methods=["GET"])
def get_progress(task_id):
    # Return progress for a specific task
    pass
'''