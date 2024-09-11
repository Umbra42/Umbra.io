import os
from cs50 import SQL
from werkzeug.utils import secure_filename
from helpers import apology

db = SQL("sqlite:///project.db")

def make_folder(upload_folder):
    if not os.path.exists(upload_folder):
        print(f"folder did not exist. making upload folder: {upload_folder}")
        os.makedirs(upload_folder)

def get_paths(upload_files, upload_folder):
    print(" > get_files called\nfilepaths: \n")
    file_paths = []
    for i, file in enumerate(upload_files):
        filename = secure_filename(file.filename)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        file_paths.append(file_path)
        print(f"created filepath #{i} {file_path}")
    print("returning filepaths")
    return file_paths       

def is_unique(file_name, upload_path):
    print(" > is_unipue called")
    print("check for file duplicates")
    database = db.execute("SELECT * FROM files WHERE name = ?", file_name)
    path = os.path.join(upload_path, file_name)
    print(os.path.exists(os.path.join(upload_path, file_name)))
    print(len(database), path, '\n', database)
    if os.path.exists(path) and not len(database) == 0:
        print("file already exists")
        return False
    print("is unique")
    return True

def commit(path, file_name, file_type):
    print(" > commit called")
    print("determening file size")
    file_size = str(round((os.path.getsize(path) / 1000))) + " KB"
    try:
        print(f"commit {file_size} to database")
        db.execute("INSERT INTO files (name, path, type, size) VALUES (?, ?, ?, ?)", 
                   file_name, path, file_type, file_size)
    except Exception as e:
        print(f"failed to commit: {e}")
        return apology(f"An error occurred: {e}", 500)