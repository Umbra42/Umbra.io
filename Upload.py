import os
import stat
from werkzeug.utils import secure_filename
from helpers import apology
from extensions import socketio, db, UPLOAD_PROGRESS_TRACKER
from flask import current_app

def make_folder(folder):
    if not os.path.exists(folder):
        print(f"folder did not exist. making upload folder: {folder}")
        os.makedirs(folder)
        os.chmod(folder, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
    print(f"folder found at: {folder}")
    return folder

def get_paths(upload_files, upload_folder):
    print(f" > get_paths called with: \n{upload_files}, \n{upload_folder}\n")
    file_paths = []
    for i, file in enumerate(upload_files):
        filename = secure_filename(file.filename)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        file_paths.append(file_path)
        print(f" created filepath #{i}: {file_path}")
    print(" returning filepaths")
    return file_paths       

def is_unique(file_name):
    with current_app.app_context():
        print(" > is_unique called")
        print("check for file duplicates")
        file_index = current_app.config.get("FILE_INDEX", {})
        file_path = os.path.join('files', file_name)
        result = db.execute("SELECT * FROM files WHERE name = ?", (file_name,))
        print(result)
        print(file_path)
        print(os.path.exists(file_path))
        if file_name in file_index or len(result) > 0:
            print("file already exists")
            return False
        print("is unique")
        return True

def is_allowed(file):
    return file.lower().rsplit(".", 1)[-1] in current_app.config["ALLOWED_EXTENSIONS"]

    
def commit(task_id, file, destination_path, file_name, file_type):
    with current_app.app_context():
        print(" > commit called")      
        update_progress(task_id, status= 'checking file size')
        file_size = str(round((os.path.getsize(destination_path) / 1000))) + " KB"
        try:
            print(f"commit {file_size} to database")
            update_progress(task_id, status= f'commiting {destination_path}, {file_type}, {file_size} to database')
            with db:
                db.execute("INSERT INTO files (name, path, type, size) VALUES (?, ?, ?, ?)", 
                    file_name, destination_path, file_type, file_size)

            current_app.config["FILE_INDEX"][file_name] = destination_path
            file.save(os.path.join(destination_path, secure_filename(file_name)))
        except Exception as e:
            print(f"failed to commit: {e}")
            update_progress(task_id, status=f'failed to commit with error: {e}', state="ERROR")
            return apology(f"An error occurred: {e}", 500)
        
def update_progress(task_id, **updates):
    if task_id not in UPLOAD_PROGRESS_TRACKER:
        UPLOAD_PROGRESS_TRACKER[task_id] = {
            "task_id" : "",
            "state" : 'Initializing',
            "total" : '',
            "current" : "",
            "current_n" : 0,
            "step_n": 1,
            "status" : 'Init upload...'
        }
    UPLOAD_PROGRESS_TRACKER[task_id]["step_n"] += 1
    UPLOAD_PROGRESS_TRACKER[task_id].update(updates)
    socketio.emit("progress_update", UPLOAD_PROGRESS_TRACKER[task_id])

def build_index(root):
    file_index = {}
    for root, _, files in os.walk(root):
        for file in files:
            file_index[file] = os.path.join(root, file)
    return file_index
