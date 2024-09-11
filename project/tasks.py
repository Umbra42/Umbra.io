import os
import Blender
from upload import commit, is_unique
from app import celery

@celery.task(bind=True)
def start_upload(self, N_upload_files, upload_folder, file_paths, system):
    self.update_state(
        state='PROGRESS', 
        meta={
            'current': 0, 
            'total': N_upload_files, 
            'status': 'Init upload...'
            }
        )
    
    print(f" > start_upload called with: \n{N_upload_files}, \n{upload_folder}, \n{file_paths}, \n{system}")

    try:
        self.update_state(
        state='PROGRESS', 
        meta={
            'current': 0, 
            'total': N_upload_files, 
            'status': 'Indexing files...'
            }
        )
        for i, file_path in enumerate(file_paths):
            file_name = os.path.basename(file_path)
            file_type = os.path.splitext(file_name)[1]
            self.update_state(
            state='PROGRESS', 
            meta={
                'current': f"{i} {file_name} {file_type}", 
                'total': N_upload_files, 
                'status': 'Indexing files...'
                }
            )
            
            match file_type:
                case ".blend":
                    print(f"found {file_type}")
                    self.update_state(
                    state='PROGRESS', 
                    meta={
                        'current': f"{i} {file_name} {file_type}", 
                        'total': N_upload_files, 
                        'status': 'Starting conversion to glb...'
                        }
                    )
                    upload_path = os.path.join(upload_folder, "display_objects")
                    print(f"going to upload to: {upload_path}")
                    print(" > calling convert")
                    file_name = convert(upload_path, file_name, system)

                case ".md" | ".txt" | ".docx" | ".doc" | ".xlsx" | ".xlsm":
                    print(f"found {file_type}")
                    upload_path = os.path.join(upload_folder, "text", file_name)
                    print(f"going to upload to: {upload_path}")

                case _:
                    print(f"found {file_type}")
                    upload_path = os.path.join(upload_folder, "images", file_name)
                    print(f"going to upload to: {upload_path}")

            print(" > calling is_unique")
            if is_unique(file_name, upload_path):
                self.update_state(
                    state='PROGRESS', 
                    meta={
                        'current': f"{i} {file_name} {file_type}", 
                        'total': N_upload_files, 
                        'status': 'Checking file existence in database...'
                        }
                    )   
                path = os.path.join(upload_path, file_name)
                print("uploaded to: ", path)
                self.update_state(
                    state='PROGRESS', 
                    meta={
                        'current': f"{i} {file_name} {file_type}", 
                        'total': N_upload_files, 
                        'status': f'Appending file to {path}...'
                        }
                    )
                with open(file_path, 'rb') as source_file:
                    with open(path, 'wb') as dest_file:
                        dest_file.write(source_file.read())
                print(" > calling commit")
                self.update_state(
                    state='PROGRESS', 
                    meta={
                        'current': f"{i} {file_name} {file_type}", 
                        'total': N_upload_files, 
                        'status': 'commiting file location to database...'
                        }
                    )
                commit.apply_async(args=[path, file_name, file_type])
            
            print("feeding progress to celery")
            
            self.update_state(state='PROGRESS', meta={
                'current': i+1, 
                'total': N_upload_files, 
                'status': 'Uploading file completed...'
                })

        self.update_state(
            state='PROGRESS', 
            meta={
                'current': i, 
                'total': N_upload_files, 
                'status': 'Task completed!', 
                'result': 42
            }
        )    
        return
    
    except Exception as e:
        return {'current':1, 'total': 1, 'status': 'Failed', 'error': str(e)}   

@celery.task(bind=True)
def convert(self, upload_path, file_name, system):
    # check for blender installation
    print(" > convert called")
    print(" > calling make_Blender")
    print(system)
    blender = Blender.make_blender(system)
    print("blender: ", blender)
    file_GLB = os.path.splitext(file_name)[0] + ".glb"
    print(file_GLB)
    print(upload_path)
    uploaded_file = os.path.join(upload_path, file_name)
    if is_unique(file_GLB, upload_path):
        object_path = os.path.join(upload_path, file_GLB)
        Blender.run_conversion(uploaded_file, object_path, blender)
        print("file converted")
    return file_GLB

@celery.task(bind=True)
