import os
import urllib
import zipfile
import tarfile
import subprocess
from flask import current_app
from extensions import UPLOAD_PROGRESS_TRACKER
from Upload import update_progress
    
def blender_exists(path):
    print(f"checking for blender at {path}")
    exe_name = "blender.exe" if os.name == "nt" else "blender"
    for folder in os.listdir(path):
        folder_path = os.path.join(path, folder)
        if folder.strip().lower().startswith("blender") and os.path.isdir(folder_path):
            for file in os.listdir(folder_path):
                if file.strip().lower() == exe_name:
                    blender_path = os.path.join(folder_path, file)
                    print(f"found blender at: {blender_path}")
                    return blender_path

    print("blender not found")
    return None 
    
def download_blender(url):
    file_name = url.rstrip('/').split('/')[-1]
    compressed_path = os.path.join(current_app.config['APPS_PATH'], file_name)    
    try:
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
            }
        )
        with urllib.request.urlopen(req) as response, open(compressed_path, 'wb') as out_file:
            out_file.write(response.read())
    except Exception as e:
        print(f"error during download: {e}")
        return None

    return compressed_path

def extract_to(compressed_path):
    print(f"extracting from {compressed_path} to {current_app.config['APPS_PATH']}")
    if not compressed_path and not os.path.exists(compressed_path):
        print(f"{compressed_path} did not exist or is invalid") 
    else:
        match current_app.config['SYSTEM']:
            case "Windows":
                try:
                    with zipfile.ZipFile(compressed_path, 'r') as zip_ref:
                        zip_ref.extractall(current_app.config['APPS_PATH'])
                    print(f"install complete: {compressed_path}")
                    os.remove(compressed_path)
                    print(f"File {compressed_path} has been removed successfully")
                    path = compressed_path.rstrip(".zip")
                    return path

                except zipfile.BadZipFile:
                    print("not a valid zip")
            
            case "Linux":
                try:
                    with tarfile.open(compressed_path, 'r:xz') as tar_ref:
                        tar_ref.extractall(current_app.config['APPS_PATH'])
                    print(f"Extraction complete: {current_app.config['APPS_PATH']}")
                    os.remove(compressed_path)
                    print(f"File {compressed_path} has been removed successfully")
                    path = compressed_path.rstrip(".tar1")
                    return tar_ref

                except Exception as e:
                    print(f"Error extracting tarball: {e}")
                    raise
    

def run_conversion(task_id, input, output, path):
    try:
        print(f" > run_converion called with: \n upload_progress: {UPLOAD_PROGRESS_TRACKER[task_id]} \n inputpath: {input}\n outputpath: {output}\n blenderpath: {path}\n")
        update_progress(task_id, status='running conversion script', state='converting')
        script_path = os.path.join(os.getcwd(), 'scripts', 'convert.py')
        print(f" script: {script_path}\n")
        command = [ 
            path,
            '--background', 
            '--python', 
            script_path,
            '--',
            input,
            output,
        ]
        print(f" command: {command}\n")

        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        print("Blender output:", result.stdout)
        print("Blender errors:", result.stderr)
        if result.returncode != 0:
            print("Error: Blender conversion failed")
            return False
        print("Conversion successful.")
    except subprocess.CalledProcessError as e:
        print(f"Blender script failed with return code: {e.returncode}")
        return False
    except PermissionError:
        print(f"You do not have permissions to save the converted file here: {output}")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    return True

def start_blender_listener(app):
    script = os.path.join(os.getcwd(), 'scripts', 'blender_listener.py')
    blender = app.config["BLENDER_PATH"]
    upload_folder = app.config["PROCESS_FOLDER"]
    display_folder = app.config["MODELS_FOLDER"]

    subprocess.Popen([blender, "--background", "--python", script, "--", upload_folder, display_folder])



