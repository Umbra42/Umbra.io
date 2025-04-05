import os
import time
from Upload import commit, update_progress
from extensions import UPLOAD_PROGRESS_TRACKER
from Blender import blender_exists

def init_blender(app):
    update_progress(status="Checking Blender installation")
    with app.app_context():
        try:
            blender_path = blender_exists(app.config['APPS_PATH'])
            print(f"Blender initialized at {blender_path}")
            return blender_path
        except Exception as e:
            print(f"Failed to initialize Blender: {e}")
            raise

def start_upload(app, task_id, upload_files, destinations):
    with app.app_context():
        print(f" > start_upload called")
        update_progress(task_id, state= "Running", status= 'Indexing files...', step_n=0)
        for i, file in enumerate(upload_files):
            file_name = file.filename.replace(" ", "_")
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

            update_progress(task_id, status="awaiting conversion", state="Waiting")
            timeout = 60
            start_time = time.time()
            while not os.path.exists(upload_path):
                if time.time() - start_time > timeout:
                    print("blender timedout")
                    raise TimeoutError
                time.sleep(2)

            print(" > calling commit")
            update_progress(task_id, status='commiting file name and location to database', state="Finalizing")
            commit(task_id, file, upload_path, file_name, file_type)
      
        update_progress(task_id, status= 'Upload successful', state= 'Complete')
        if task_id in UPLOAD_PROGRESS_TRACKER:
            del UPLOAD_PROGRESS_TRACKER[task_id]
        return