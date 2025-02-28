from flask import Blueprint, request, jsonify, session, current_app
from extensions import socketio, upload_tasks
from helpers import login_required
from Upload import get_paths, is_unique
import uuid
import tasks

upload_bp = Blueprint('upload', __name__)

@upload_bp.route("/upload", methods=["POST"])
@login_required
def upload():
    print(" > /upload called")
    
    upload_progress = {
        "task_id" : "",
        "state" : 'Initializing',
        "total" : '',
        "current" : "",
        "current_n" : 0,
        "step_n": 1,
        "status" : 'Init upload...'
    }
    
    try:
        upload_progress['status'] = 'getting file list...'
        socketio.emit('progress_update', upload_progress)
        upload_files = request.files.getlist('files')
        
        upload_progress['step_n'] += 1
        upload_progress['status'] = 'determining list length...'
        socketio.emit('progress_update', upload_progress)
        if len(upload_files) <= 0:
            return jsonify({"error": "No files uploaded"}), 400
        N_upload_files = len(upload_files)
        upload_progress['total'] = N_upload_files

        upload_progress['step_n'] += 1
        upload_progress['status'] = 'verifying upload location...'
        socketio.emit('progress_update', upload_progress)
        upload_folder = current_app.config['UPLOAD_FOLDER']
        upload_progress['status'] = f'upload location at {upload_folder}...'
        socketio.emit('progress_update', upload_progress)
        print(upload_folder)
        
        upload_progress['step_n'] += 1
        upload_progress['status'] = 'constructing filepaths...'
        socketio.emit('progress_update', upload_progress)
        print(" > making filepaths for temp upload.\ncalling get_paths")
        file_paths = get_paths(upload_files, upload_folder) 
        print(f"returned filepaths:\n{file_paths}")
        upload_progress['status'] = f'consftucted paths: {file_paths}...'
        socketio.emit('progress_update', upload_progress)
        
        upload_progress['step_n'] += 1
        upload_progress['status'] = 'checking file uniqueness...'
        socketio.emit('progress_update', upload_progress)
        for file_path in file_paths:
            if not is_unique(file_path):
                return jsonify({"error": "File already exists", "filename": file_path}), 409
        
        upload_progress['step_n'] += 1
        upload_progress['status'] = 'generating task id...'
        socketio.emit('progress_update', upload_progress)
        task_id = str(uuid.uuid4())
        print(f"Generated task ID: {task_id}")
        upload_progress['task_id'] = task_id
        session['task_id'] = task_id
        upload_progress['status'] = 'task id generated...'
        socketio.emit('progress_update', upload_progress)


        upload_progress['step_n'] += 1
        upload_progress['status'] = 'starting upload...'
        socketio.emit('progress_update', upload_progress)
        print(f" > calling start_upload with:\n task_id:{task_id}, \n N_upload_files:{N_upload_files}, \n upload_folder:{upload_folder}, \n file_paths:{file_paths}")        
        socketio.start_background_task(tasks.start_upload, current_app._get_current_object(), upload_progress, task_id, N_upload_files, upload_folder, file_paths)
            
        return jsonify(upload_progress), 200
    
    except Exception as e:
        print(f"❌ Upload Error: {str(e)}")
        upload_progress['state'] = "Error"
        upload_progress['status'] = f"Failed to upload files: {str(e)}"
        return jsonify(upload_progress), 500

@upload_bp.route("/progress/<task_id>", methods=["GET"])
def upload_progress(task_id):
    # Return progress for a specific task
    progress = upload_tasks.get(task_id)
    if progress:
        return jsonify(progress), 200
    else:
        return jsonify({"error": "Task not found"}), 404