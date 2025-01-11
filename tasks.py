import os
from Upload import commit, is_unique, make_folder
from extensions import socketio
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

def start_upload(app, upload_progress, task_id, N_upload_files, upload_folder, file_paths):
    with app.app_context():
        socketio.emit('progress_update', upload_progress)
        print(f" > start_upload called with:\n task_id:{task_id}, \n N_upload_files:{N_upload_files}, \n upload_folder:{upload_folder}, \n file_paths:{file_paths}")

        upload_progress['status'] = 'Indexing files...'
        for i, file_path in enumerate(file_paths):
            file_name = os.path.basename(file_path)
            file_type = os.path.splitext(file_name)[1]
            current = f"{i} {file_name} {file_type}"
            upload_path = None
            upload_progress['current'] = current  
            socketio.emit('progress_update', upload_progress)
            
            match file_type:
                case ".blend":
                    print(f"found {file_type}")
                    
                    upload_progress['overall'] += 1
                    upload_progress['current'] = current
                    upload_progress['status'] = 'Starting conversion to glb...'
                    socketio.emit('progress_update', upload_progress)
                    
                    print(f"constructing conversion environment")
                    upload_display_folder = os.path.join(upload_folder, "display_objects")
                    print(f" > calling make_folder")
                    make_folder(upload_display_folder)
                    print(f"going to upload to: {upload_display_folder}")
                    
                    print(" > calling convert")
                    file_name = convert(upload_progress, upload_display_folder, file_name, current_app)
                    upload_path = os.path.join(upload_display_folder, file_name) 

                case ".md" | ".txt" | ".docx" | ".doc" | ".xlsx" | ".xlsm":
                    print(f"found {file_type}")

                    upload_progress['overall'] += 1
                    upload_progress['current'] = current
                    upload_progress['status'] = 'setting upload path'
                    socketio.emit('progress_update', upload_progress)  

                    upload_path = os.path.join(upload_folder, "text", file_name)
                    print(f"going to upload to: {upload_path}")

                case _:
                    print(f"found {file_type}")

                    upload_progress['overall'] += 1
                    upload_progress['current'] = current
                    upload_progress['status'] = 'setting upload path'
                    socketio.emit('progress_update', upload_progress)

                    upload_path = os.path.join(upload_folder, "images", file_name)
                    print(f"going to upload to: {upload_path}")

            print(" > calling is_unique")
            
            upload_progress['status'] = 'checking file uniqueness'
            socketio.emit('progress_update', upload_progress)

            
            if is_unique(upload_path):
                path = os.path.join(upload_path)
                print("uploaded to: ", path)
                with open(file_path, 'rb') as source_file:
                    with open(path, 'wb') as dest_file:
                        dest_file.write(source_file.read())
                print(" > calling commit")

                upload_progress['status'] = 'commiting file name and location to database'
                socketio.emit('progress_update', upload_progress)

                commit(socketio, upload_progress, path, file_name, file_type)
            else:
                upload_progress['status'] = 'file already exists'
                socketio.emit('progress_update', upload_progress)

            upload_progress['status'] = 'Upload successful'
            socketio.emit('progress_update', upload_progress)
        
        return