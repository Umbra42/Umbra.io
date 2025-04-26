import os
import subprocess
import sys
from Upload import commit, update_progress, blender_progress, init_progress_tracker
from extensions import UPLOAD_PROGRESS_TRACKER, WATCHER_PROCESS, socketio
from Blender import blender_exists, install_blender, is_running, relay
from flask import current_app

def init_blender(app, emit=True):  
    if "blender" not in UPLOAD_PROGRESS_TRACKER:
        init_progress_tracker(task_id="blender")

    if emit: blender_progress(status="Checking Blender installation")

    with app.app_context():
        try:
            blender_path = blender_exists(app.config['APPS_PATH'], emit=emit)
            if blender_path is None:
                if emit: blender_progress(status="Blender Not found", state="Initializing")
                blender_path = install_blender(app)
            if emit: blender_progress(status="Blender found", state="Complete")
            print(f"Blender initialized at {blender_path}")
            return blender_path
        except Exception as e:
            if emit:
                blender_progress(status="Blender not found", state="Error")
            print(f"Failed to initialize Blender: {e}")
            raise

def launch_listener():
    global WATCHER_PROCESS
    if is_running(WATCHER_PROCESS):
        blender_progress(status="Blender Listener already running")
        return

    blender_progress(status="Passing data to and starting Blender Listener script")
    blender = current_app.config["BLENDER_PATH"]
    script = os.path.join(os.getcwd(), 'scripts', 'blender_listener.py')
    process_folder = current_app.config["PROCESS_FOLDER"]
    glb_folder = current_app.config["MODELS_FOLDER"]
    
    cmd = [
        sys.executable, 
        script,
        "--blender_exe", blender,
        "--process_folder", process_folder,
        "--glb_folder",  glb_folder, 
        "--server_url", "http://127.0.0.1:5000",
    ]         
    print(f"Blender Listener started with command: {cmd}")
    
    WATCHER_PROCESS = subprocess.Popen(
        cmd, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE, 
        text=True, 
        bufsize=1)
    print(f"Blender Listener started with PID: {WATCHER_PROCESS.pid}")
  
    socketio.start_background_task(relay, WATCHER_PROCESS.stdout, "OUT")
    socketio.start_background_task(relay, WATCHER_PROCESS.stderr, "ERR")

def terminat_listener():
    blender_progress(status="Terminating Blender Listener")
    global WATCHER_PROCESS
    if is_running(WATCHER_PROCESS):
        WATCHER_PROCESS.terminate()
        WATCHER_PROCESS.wait()
        WATCHER_PROCESS = None
        blender_progress(status="Blender Listener Termninated")

def start_upload(app, task_id, upload_files, destinations):
    with app.app_context():
        print(f" > start_upload called")
        update_progress(task_id, state= "Running", status= 'Indexing files...', step_n=0)
        for i, file_obj in enumerate(upload_files):
            file_name = file_obj.filename.replace(" ", "_")
            file_type = os.path.splitext(file_name)[1]
            current = f"{file_name} {file_type}"
            current_n = i
            upload_path = None
            update_progress(task_id, status=f'indexing file:{current}...', current_file_name = current, current_file_n = current_n)
            update_progress(task_id, status='matching file type...')
            match file_type:
                case ".blend":
                    print(f"found {file_type}")             
                    update_progress(task_id, status='Starting conversion to glb...', state='Converting')
                    destination = destinations["models"]
                    file_name = os.path.join(os.path.splitext(file_name)[0] + ".glb")
                    print("glb file name: ", file_name)
                    update_progress(task_id, status='setting upload path', state='Processing')
                    upload_path = os.path.join(destination, file_name) 
                    print(f"going to upload to: {upload_path}")
                    update_progress(task_id, status="awaiting conversion", state="Waiting")

                case ".md" | ".txt" | ".docx" | ".doc" | ".xlsx" | ".xlsm":
                    print(f"found {file_type}")
                    update_progress(task_id, status='setting upload path', state='Processing')
                    destination = destinations["projects"]
                    upload_path = os.path.join(destination, "text", file_name)
                    print(f"going to upload to: {upload_path}")
                    print(" > calling commit")
                    update_progress(task_id, status='commiting file name and location to database', state="Finalizing")
                    commit(task_id, file_obj, upload_path, file_name, file_type)

                case _:
                    print(f"found {file_type}")
                    update_progress(task_id, status= 'setting upload path', state='Processing')
                    destination = destinations["code"]
                    upload_path = os.path.join(destination, "images", file_name)
                    print(f"going to upload to: {upload_path}")
                    print(" > calling commit")
                    update_progress(task_id, status='commiting file name and location to database', state="Finalizing")
                    commit(task_id, file_obj, upload_path, file_name, file_type)


        update_progress(task_id, status= 'Upload successful', state= 'Complete')
        if task_id in UPLOAD_PROGRESS_TRACKER:
            del UPLOAD_PROGRESS_TRACKER[task_id]
        return