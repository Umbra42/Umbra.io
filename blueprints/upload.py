from flask import Blueprint, request, jsonify, session, current_app
from extensions import socketio, UPLOAD_PROGRESS_TRACKER
from helpers import login_required
from Upload import get_paths, is_unique, is_allowed, update_progress
import uuid
import tasks

upload_bp = Blueprint('upload', __name__)

@upload_bp.route("/upload", methods=["POST"])
@login_required
def upload():
    print(" > /upload called")
    try:
        task_id = str(uuid.uuid4())
        session['task_id'] = task_id
        update_progress(task_id, status='Initializing Upload...', state='Processing')  
        print(f"Generated task ID: {task_id}")
        update_progress(task_id, status='getting file list...')
        upload_files = request.files.getlist('files')
        
        update_progress(task_id, state='validating files and environment')
        upload_files[:] = [file for file in upload_files if is_allowed(file.filename) and is_unique(file.filename)] 
        N_upload_files = len(upload_files)
        update_progress(task_id, status='determining list length...', total= N_upload_files)
        if N_upload_files <= 0:
            return jsonify({"error": "No files uploaded"}), 400
        
        update_progress(task_id, status='verifying upload location...')
        process_folder = current_app.config['PROCESS_FOLDER']
        destinations = {
            "models": current_app.config['MODELS_FOLDER'], 
            "code": current_app.config["CODE_FOLDER"], 
            "projects": current_app.config["PROJECTS_FOLDER"]
        }
        update_progress(task_id, status= f'upload process location at {process_folder} ...\n             upload display location at{destinations}...')        

        update_progress(task_id, status='constructing filepaths...', state='Processing')
        print(" > making filepaths for temp upload.\n   calling get_paths")
        file_paths = get_paths(upload_files, process_folder) 
        print(f"returned filepaths:\n{file_paths}")
        update_progress(task_id, status= f'constructed paths: {file_paths}...')        

        update_progress(task_id, status='starting upload...')
        print(f" > calling start_upload with:\n task_id:{task_id}, \n upload_files:{upload_files}, \n N_upload_files:{N_upload_files}, \n process_folder:{process_folder}, \n file_paths:{file_paths}")        
        socketio.start_background_task(tasks.start_upload, current_app._get_current_object(), task_id, upload_files, N_upload_files, process_folder, destinations, file_paths)
            
        return jsonify(UPLOAD_PROGRESS_TRACKER[task_id]), 200
    
    except Exception as e:
        print(f"❌ Upload Error: {str(e)}")
        update_progress(task_id, status=f"Failed to upload files: {str(e)}", state="Error")
        return jsonify(UPLOAD_PROGRESS_TRACKER[task_id]), 500

@upload_bp.route("/progress/<task_id>", methods=["GET"])
def upload_progress(task_id):
    # Return progress for a specific task
    progress = UPLOAD_PROGRESS_TRACKER.get(task_id)
    if progress:
        return jsonify(progress), 200
    else:
        return jsonify({"error": "Task not found"}), 404