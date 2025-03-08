import os
from Upload import commit, update_progress
from extensions import socketio, UPLOAD_PROGRESS_TRACKER
from flask import current_app
from blueprints.blender import convert, check_blender

def init_blender(app):
    with app.app_context():
        try:
            blender_path = check_blender(app)
            print(f"Blender initialized at {blender_path}")
            return blender_path
        except Exception as e:
            print(f"Failed to initialize Blender: {e}")
            raise

def start_upload(app, task_id, upload_files, N_upload_files, process_folder, destinations, file_paths):
    with app.app_context():
        print(f" > start_upload called with:\n task_id:{task_id}, \n N_upload_files:{N_upload_files}, \n process_folder:{process_folder}, \n file_paths:{file_paths}")
        update_progress(task_id, state= "Running", status= 'Indexing files...')
        for i, file in enumerate(upload_files):
            file_name = file.filename.replace(" ", "_") 
            file_type = os.path.splitext(file_name)[1]
            current = f"{file_name} {file_type}"
            current_n = i
            upload_path = None
            update_progress(task_id, status=f'indexing file:{current}...', current= current, current_n=current_n)
            update_progress(task_id, status='matching file type...')
            match file_type:
                case ".blend":
                    print(f"found {file_type}")             
                    update_progress(task_id, status='Starting conversion to glb...', state='Converting')
                    print(" > calling convert")
                    destination = destinations["models"]
                    file_name = convert(task_id, destination, file_name, current_app)
                    update_progress(task_id, status='setting upload path', state='Processing')
                    upload_path = os.path.join(destination, file_name) 
                    print(f"going to upload to: {upload_path}")

                case ".md" | ".txt" | ".docx" | ".doc" | ".xlsx" | ".xlsm":
                    print(f"found {file_type}")
                    update_progress(task_id, status='setting upload path', state='Processing')
                    destination = destinations["projects"]
                    upload_path = os.path.join(destination, "text", file_name)
                    print(f"going to upload to: {upload_path}")

                case _:
                    print(f"found {file_type}")
                    update_progress(task_id, status= 'setting upload path', state='Processing')
                    destination = destinations["code"]
                    upload_path = os.path.join(destination, "images", file_name)
                    print(f"going to upload to: {upload_path}")

            print(" > calling commit")
            update_progress(task_id, status='commiting file name and location to database', state="Finalizing")
            commit(task_id, file, upload_path, file_name, file_type)
      
        update_progress(task_id, status= 'Upload successful', state= 'Complete')
        if task_id in UPLOAD_PROGRESS_TRACKER:
            del UPLOAD_PROGRESS_TRACKER[task_id]
        return