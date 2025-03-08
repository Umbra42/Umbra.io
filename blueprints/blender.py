import os
from flask import Blueprint
from Blender import blender_exists, download_blender, extract_to, run_conversion
from Upload import is_unique, update_progress
from extensions import UPLOAD_PROGRESS_TRACKER

blender_bp = Blueprint('blender', __name__)

@blender_bp.route("/check", methods=["GET"])
def check_blender(app):
    with app.app_context():
        blender_path = blender_exists(app.config['APPS_PATH'])
        if not blender_path :
            blender_path = install_blender(app)
            print(blender_path)
        return blender_path

@blender_bp.route("/install", methods=["POST"])
def install_blender(app):
    if app.config['SYSTEM'] == "Windows":
        url = "https://ftp.nluug.nl/pub/graphics/blender/release/Blender4.1/blender-4.1.0-windows-x64.zip"        
    elif app.config['SYSTEM'] == "Linux":
        url = "https://ftp.nluug.nl/pub/graphics/blender/release/Blender4.1/blender-4.1.0-linux-x64.tar.xz"
    
    match app.config['SYSTEM']:
        case "Windows":
            print("downloading zip for windows")
            compressed_path = download_blender(url)            
            exe_path = extract_to(compressed_path)

        case "Linux":
            print("downloading zip for linux")
            compressed_path = download_blender(url)
            exe_path = extract_to(compressed_path)

        case _:
            print(f"Unsupported system: {app.config['SYSTEM']}")
    return exe_path

@blender_bp.route("/convert", methods=["POST"])
def convert(task_id, destination, file_name, app):
    update_progress(task_id, status='constructing conversion object...')
    blender_path = app.config['BLENDER_PATH']
    process_folder = app.config['PROCESS_FOLDER']
    file_GLB = os.path.splitext(file_name)[0] + ".glb"
    uploaded_file = os.path.join(process_folder, file_name)
    print("uploaded_file: ", uploaded_file)
    destination_path = os.path.join(destination, file_GLB)

    if is_unique(destination_path):
        update_progress(task_id, status='checking object uniqueness...', state='Verifying')
        print(f" > calling run_conversion with: \n upload_progress: {UPLOAD_PROGRESS_TRACKER[task_id]}\n uploaded_file: {uploaded_file}\n destination_path: {destination_path}\n blender_path: {blender_path}")
        if not run_conversion(task_id, uploaded_file, destination_path, blender_path):
            print("conversion failed")
        else:
            print("file converted")
        
    return file_GLB

