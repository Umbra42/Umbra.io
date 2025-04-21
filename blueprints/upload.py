import uuid
import tasks
import os
from extensions import socketio, UPLOAD_PROGRESS_TRACKER
from flask import Blueprint, request, jsonify, session, current_app
from flask_socketio import emit
from helpers import login_required
from Upload import process_paths, is_unique, is_allowed, update_progress, init_progress_tracker, commit

upload_bp = Blueprint('upload', __name__)

@upload_bp.route("/upload", methods=["POST"])
@login_required
def upload():
    print(" > /upload called")
    try:
        task_id = str(uuid.uuid4())
        init_progress_tracker(task_id)
        session['task_id'] = task_id
        update_progress(task_id, status='Initializing Upload...', state='Pending')  
        print(f"Generated task ID: {task_id}")
        update_progress(task_id, status='getting file list...')
        upload_files = request.files.getlist('files')
        
        update_progress(task_id, status='validating files and environment')
        upload_files[:] = [file for file in upload_files if is_allowed(file.filename) and is_unique(file.filename)] 
        N_upload_files = len(upload_files)
        update_progress(task_id, status='determining list length...', total_file_n = N_upload_files)
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

        update_progress(task_id, status='constructing filepaths...', state='Pending')
        print(" > making filepaths for temp upload.\n   calling get_paths")
        file_paths = process_paths(upload_files, process_folder) 
        print(f"returned filepaths:\n{file_paths}")
        update_progress(task_id, status= f'constructed paths: {file_paths}...')        

        update_progress(task_id, total_file_n = N_upload_files, current_file_n = 0, step_n = 0, total_step = 3, status='starting upload...')
        print(f" > calling start_upload with:\n task_id:{task_id}, \n upload_files:{upload_files}, \n N_upload_files:{N_upload_files}, \n process_folder:{process_folder}, \n file_paths:{file_paths}")        
        socketio.start_background_task(tasks.start_upload, current_app._get_current_object(), task_id, upload_files, destinations)
            
        return jsonify(UPLOAD_PROGRESS_TRACKER[task_id]), 200
    
    except Exception as e:
        print(f"❌ Upload Error: {str(e)}")
        update_progress(task_id, status=f"Failed to upload files: {str(e)}", state="Error")
        return jsonify(UPLOAD_PROGRESS_TRACKER[task_id]), 500

# TODO: corospond with litener for commit call    
@socketio.on("converted", namespace="/upload")
def on_converted(data):
    task_id = data.get("task_id")
    processed_files = data.get("processed_files", [])
    print(f"Received converted files: {processed_files} for task ID: {task_id}")
    if task_id in UPLOAD_PROGRESS_TRACKER:
        update_progress(task_id, status="Files converted", state="Complete", processed_files=processed_files)
        for file_path in processed_files:
            file_name = os.path.basename(file_path)
            commit(task_id, open(file_path, 'rb'), file_path, file_name, os.path.splitext(file_name)[1])
    else:
        print(f"Task ID {task_id} not found in progress tracker.")