import os
import stat
from werkzeug.utils import secure_filename
from helpers import apology
from extensions import db
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

def is_unique(path):
    with current_app.app_context():
        print(" > is_unique called")
        print("check for file duplicates")
        file_name = os.path.basename(path)
        database = db.execute("SELECT * FROM files WHERE name = ?", (file_name,))
        print(database)
        print(path)
        print(os.path.exists(path))
        if os.path.exists(path) and len(database) > 0:
            print("file already exists")
            return False
        print("is unique")
        return True

def is_allowed(file):
    return file.lower().rsplit(".", 1)[-1] in current_app.config["ALLOWED_EXTENSIONS"]

    
def commit(socketio, upload_progress, path, file_name, file_type):
    with current_app.app_context():
        print(" > commit called")      
        upload_progress['status'] = 'checking file size'
        socketio.emit('progress_update', upload_progress)

        file_size = str(round((os.path.getsize(path) / 1000))) + " KB"
        try:
            print(f"commit {file_size} to database")
            
            upload_progress['status'] = f'commiting {file_name}, {path}, {file_type}, {file_size} to database'
            socketio.emit('progress_update', upload_progress)
            with db:
                db.execute("INSERT INTO files (name, path, type, size) VALUES (?, ?, ?, ?)", 
                    file_name, path, file_type, file_size)
        
        except Exception as e:
            print(f"failed to commit: {e}")

            upload_progress['status'] = f'failed to commit with error: {e}'
            socketio.emit('progress_update', upload_progress)

            return apology(f"An error occurred: {e}", 500)