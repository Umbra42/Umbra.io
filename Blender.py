import os
import urllib
import zipfile
import tarfile
from flask import current_app
from Upload import blender_progress

def blender_exists(path, emit=True):
    blender_progress(status="Checking for Blender installation", emit=emit)
    print(f"checking for blender at {path}")
    exe_name = "blender.exe" if os.name == "nt" else "blender"
    for folder in os.listdir(path):
        folder_path = os.path.join(path, folder)
        if folder.strip().lower().startswith("blender") and os.path.isdir(folder_path):
            for file in os.listdir(folder_path):
                if file.strip().lower() == exe_name:
                    blender_path = os.path.join(folder_path, file)
                    blender_progress(status="Blender found", emit=emit)
                    print(f"found blender at: {blender_path}")
                    return blender_path
    blender_progress(status="Blender not found", emit=emit)
    print("blender not found")
    raise FileNotFoundError("Blender executable not found in given path") 

def install_blender():
    if current_app.config['SYSTEM'] == "Windows":
        url = "https://ftp.nluug.nl/pub/graphics/blender/release/Blender4.1/blender-4.1.0-windows-x64.zip"        
    elif current_app.config['SYSTEM'] == "Linux":
        url = "https://ftp.nluug.nl/pub/graphics/blender/release/Blender4.1/blender-4.1.0-linux-x64.tar.xz"
    
    match current_app.config['SYSTEM']:
        case "Windows":
            print("downloading zip for windows")
            compressed_path = download_blender(url)            
            exe_path = extract_to(compressed_path)

        case "Linux":
            print("downloading zip for linux")
            compressed_path = download_blender(url)
            exe_path = extract_to(compressed_path)

        case _:
            print(f"Unsupported system: {current_app.config['SYSTEM']}")
    return exe_path

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
                    return path

                except Exception as e:
                    print(f"Error extracting tarball: {e}")
                    raise

def is_running(process):
    if process and process.poll() is None:
        print("blender is running")
        return True
    print("blender is not running")
    return False


