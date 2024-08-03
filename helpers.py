import csv
import datetime
import os
import pytz
import requests
import subprocess
import urllib
import uuid
import subprocess
import winreg
import urllib.request
import zipfile
import threading

from cs50 import SQL
from celery import Celery
from flask import redirect, render_template, session, jsonify
from functools import wraps
from werkzeug.utils import secure_filename

db = SQL("sqlite:///project.db")


def make_celery(app):
    celery = Celery(
        app.import_name, 
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
        )
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def notify():
    apology("TODO", 400)


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None and session.get("is_admin") is False:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def convert(upload_path, file_name, app):
    # check for blender installation
    print("start conversion")
    system = app.config["SYSTEM"]
    if system == "Windows":
        blender_path = "Blender"
        url = "https://ftp.nluug.nl/pub/graphics/blender/release/Blender4.1/blender-4.1.0-windows-x64.zip"        
    elif system == "Linux":
        blender_path = "/usr/bin/blender/blender"
        url = "https://ftp.nluug.nl/pub/graphics/blender/release/Blender4.1/blender-4.1.0-linux-x64.tar.xz"
    
    full_blender_path = os.path.join(os.getcwd(), 'apps', blender_path)
    print(f"blender instance path: {full_blender_path}")
    if not blender_exists(full_blender_path):
        download_path = os.path.join(os.getcwd(), 'apps')
        install_blender(url, download_path, full_blender_path, system)
    
    file_GLB = os.path.splitext(file_name)[0] + ".glb"
    print(file_GLB)
    print(upload_path)
    uploaded_file = os.path.join(upload_path, file_name)
    if is_unique(file_GLB, upload_path):
        object_path = os.path.join(upload_path, file_GLB)
        run_conversion(uploaded_file, object_path, full_blender_path)
        print("file converted")
    return file_GLB


def blender_exists(path):
    if os.path.exists(path):
        print("blender found")
        return True
    print("could not find blender")
    return False


def install_blender(url, download_path, full_blender_path, system):
    print("checking system")
    match system:
        case "Windows":
            print("downloading zip")
            zip_path = download_blender(url, download_path)
            extract_to(zip_path, full_blender_path)
            return(zip_path)
        case "linux":
            # add method for linux
            print("method to be added")
            ... 


def download_blender(url, download_path):
    file_name = url.rstrip('/').split('/')[-1]
    zip_path = os.path.join(download_path, file_name)

    req = urllib.request.Request(
        url,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
    )
    with urllib.request.urlopen(req) as response, open(zip_path, 'wb') as out_file:
        data = response.read()
        out_file.write(data)
    
    return zip_path


def extract_to(zip_path, full_blender_path):
    # Extract the downloaded file
    print(f"extracting from {zip_path} to {full_blender_path}")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(full_blender_path)
        print(f"install complete: {zip_path}")
        try:
            os.remove(zip_path)
            print(f"File {zip_path} has been removed successfully")
        except FileNotFoundError:
            print("The file does not exist")
        except PermissionError:
            print("You do not have permissions to delete the file")
        except Exception as e:
            print(f"Error occurred: {e}")
    except zipfile.BadZipFile:
        apology("not a valid zip", 304)


def run_conversion(input, output, path):
    print(f"inputpath: {input}", '\n',f"outputpath: {output}", '\n', path)
    script_path = os.path.join(os.getcwd(), 'scripts', 'convert.py')
    command = [ 
        path,
        '--background', 
        '--python', script_path,
        '--',
        input,
        output,
    ]
    if os.access(output, os.W_OK):
        try:
            subprocess.run(command, check=True)
            print("Conversion successful.")
        except subprocess.CalledProcessError as e:
            print(f"Blender script failed with return code: {e.returncode}")
        except PermissionError:
            print(f"You do not have permissions to save the converted file here: {output}")
        except Exception as e:
            print(f"An error occurred: {e}")
    else:
    # Directory does not exist or is not writable
        print("Directory does not exist or is not writable")
    

def commit(path, file_name, file_type):
    print("determening file size")
    file_size = str(round((os.path.getsize(path) / 1000))) + " KB"
    try:
        print(f"commit {file_size} to database")
        db.execute("INSERT INTO files (name, path, type, size) VALUES (?, ?, ?, ?)", 
                   file_name, path, file_type, file_size)
    except Exception as e:
        print(f"failed to commit: {e}")
        return apology(f"An error occurred: {e}", 500)


def get_progress_data(): 
    return session['PROGRESS_DATA'] == {
        "currentTask": "Uploading Files",
        "overallProgress": 50,
        "fileProgress": 75,

        "blenderInstallationRequired": True,
        "blenderProgress": 20
    }


def is_admin(id):
    query_role = db.execute("SELECT role FROM users WHERE id = ?", id)
    role = query_role[0]
    if role == "admin":
        return True
    else:
        return False
    
def init(upload_folder):
    if not os.path.exists(upload_folder):
        print("folder did not exist. making upload folder :", end = '')
        os.makedirs(upload_folder)

def progress(task_id):
    task = start_upload.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # This is the exception raised
        }
    return jsonify(response)

@celery.task(bind=True)
def start_upload(self, N_upload_files, upload_files, upload_folder, app):
    try:
        for i, file in enumerate(upload_files):
            file_name = secure_filename(file.filename)
            file_type = os.path.splitext(file_name)[1]
            
            match file_type:
                case ".blend":
                    upload_path = os.path.join(upload_folder, "display_objects")
                    file_name = convert(upload_path, file_name, app)
                case ".md" | ".txt" | ".docx" | ".doc" | ".xls" | "":
                    upload_path = os.path.join(upload_folder, "text", file_name)
                case _:
                    upload_path = os.path.join(upload_folder, "images", file_name)

            if is_unique(file_name, upload_path):   
                path = os.path.join(upload_path, file_name)
                print("uploaded to: ", path)
                file.save(path)
                commit(path, file_name, file_type)
            
            self.update_state(state='PROGRESS', meta={
                'current': i+1, 
                'total': N_upload_files, 
                'status': 'Uploading..'
                })
        return {
            'current': i, 
            'total': N_upload_files, 
            'status': 'Task completed!', 
            'result': 42}
    except Exception as e:
        return {'current':1, 'total': 1, 'status': str(e)}
    

def is_unique(file_name, upload_path):
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

