import os
import stat
import time
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

def process_paths(upload_files, folder):
    print(f" > get_paths called with: \n{upload_files}, \n{folder}\n")
    file_paths = []
    for i, file in enumerate(upload_files):
        file_path = os.path.join(folder, secure_filename(file.filename))
        file_paths.append(file_path)
        file.save(file_path)
        print(f" created filepath #{i}: {file_path}")
    print(" returning filepaths")
    return file_paths       

def is_unique(file_name):
    with current_app.app_context():
        print(" > is_unique called")
        print(f"check for file duplicates: {file_name}")
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
        try:
            if not os.path.exists(destination_path):
                print(f"{destination_path} does not exists")
            file_size = str(round((os.path.getsize(destination_path) / 1000))) + " KB"
            print(f"committing: '{file_size}' in database")
            update_progress(task_id, status= f'commiting {destination_path}, {file_type}, {file_size} to database')

            db.execute(
                "INSERT INTO files (name, path, type, size) VALUES (?, ?, ?, ?)", 
                file_name, destination_path, file_type, file_size
            )
            if file_type != ".blend" and file_type != ".glb":
                with open(destination_path, "wb") as dest_file:
                    dest_file.write(file.read())
            current_app.config["FILE_INDEX"][file_name] = destination_path
            print(f"{destination_path} commited successfuly")
        except Exception as e:
            print(f"failed to commit: {e}")
            update_progress(task_id, status=f'failed to commit with error: {e}', state="ERROR")
            return apology(f"An error occurred: {e}", 500)
        
def track_step(task_id, current_file_name, step_n, total_steps, status):
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    step = { "step" : step_n, "status" : status, "time" : now }
    tracker = UPLOAD_PROGRESS_TRACKER.get(task_id, {})
    if tracker and current_file_name in tracker["files"]:
        tracker["files"][current_file_name].append(step)

def update_progress(task_id, **update):
    if task_id not in UPLOAD_PROGRESS_TRACKER:
        UPLOAD_PROGRESS_TRACKER[task_id] = {
            "state" : 'Initializing',
            "total_file_n" : "",
            "files" : {},
            "current_file_name" : "",
            "current_file_n" : 0,
            "step_n": 0,
            "total_steps": calculate_total_steps(update),
            "status" : 'Init upload...'
        }
    UPLOAD_PROGRESS_TRACKER[task_id]["step_n"] += 1
    UPLOAD_PROGRESS_TRACKER[task_id].update(update)
    socketio.emit("progress_update", UPLOAD_PROGRESS_TRACKER[task_id])

def build_index(root):
    file_index = {}
    for root, _, files in os.walk(root):
        for file in files:
            file_index[file] = os.path.join(root, file)
    return file_index

# todo: correct;lty calculate total steps
def calculate_total_steps(update):
    n_files = update.get("total_file_n", 0)
    steps_per_file = 3
    remaining_steps = 1
    
    total_steps = (n_files * steps_per_file) + remaining_steps
    return total_steps