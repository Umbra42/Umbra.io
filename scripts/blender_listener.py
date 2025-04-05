import bpy
import json
import os
import time
import sys
import requests

def get_progress(TASK_ID):
    try:
        response = requests.get(f"http://127.0.0.1:5000/upload/progress/{TASK_ID}")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get progress for {TASK_ID}")
            return None
    except Exception as e:
        print(f"Failed to get progress for {TASK_ID}: {e}")
        return None
    
def report_progress(TASK_ID, **kwargs):
    try:
        payload = {
            "state": INIT_PROGRESS["state"],
            "total_file_n": INIT_PROGRESS["total_file_n"],
            "current_file_name": INIT_PROGRESS["current_file_name"],
            "current_file_n": INIT_PROGRESS["current_file_n"],
            "step_n": INIT_PROGRESS["step_n"],
            "total_steps": INIT_PROGRESS["total_steps"],
            "status": INIT_PROGRESS["status"]
        }
        if "current_file_name" in kwargs:
            current_file = kwargs["current_file_name"]
            
            # Build the step progress record
            step_info = {
                "step": kwargs.get("step_n"),
                "status": kwargs.get("status"),
                "time": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # If files tracking doesn't exist yet, add it
            if "files" not in INIT_PROGRESS or not isinstance(INIT_PROGRESS["files"], dict):
                INIT_PROGRESS["files"] = {}

            # If the current file hasn't been seen before, initialize its entry
            if current_file not in INIT_PROGRESS["files"]:
                INIT_PROGRESS["files"][current_file] = []

            # Append this step to that file's step history
            INIT_PROGRESS["files"][current_file].append(step_info)

            # Also update payload being sent to server
            payload["files"] = INIT_PROGRESS["files"]
            print(payload)
        requests.post(f"http://127.0.0.1:5000/upload/progress/{TASK_ID}", json=payload)
            
    except Exception as e:
        print(f"Failed to report progress: {e}")
        import traceback
        traceback.print_exc()
    
def process_new_files():
    """Check for new .blend files and convert them"""
    for filename in os.listdir(PROCESS_FOLDER):
        if filename.endswith(".blend") and filename not in processed:
            blend_path = os.path.join(PROCESS_FOLDER, filename)
            glb_output = os.path.join(GLB_FOLDER, filename.replace(".blend", ".glb"))
            report_progress(TASK_ID, status= f"Converting {filename}...", current_file_name = filename, state="Converting")
            print(f"Processing {blend_path} -> {glb_output}")

            try:
                bpy.ops.wm.open_mainfile(filepath=blend_path)
                bpy.ops.export_scene.gltf(filepath=glb_output, export_format='GLB')
                report_progress(TASK_ID, f"Converted {filename}", current_file_name =filename.replace(".blend", ".glb"), state="Done")
                print(f"Successfully converted: {blend_path}")
                processed.append(filename)
                os.remove(blend_path)  
            except Exception as e:
                print(f"Failed to process {blend_path}: {e}")
        
def track_step(task_id, current_file_name, step_n, total_steps, status):
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    step = { "step" : step_n, "status" : status, "time" : now }
    tracker = INIT_PROGRESS.get(task_id, {})
    if tracker and current_file_name in tracker["files"]:
        tracker["files"][current_file_name].append(step)

def validate_args():  
    if "--" in sys.argv:
        args = sys.argv[sys.argv.index("--") + 1:]
        print(f"ARGS: {args}")
    else:
        print("Error: Missing '--' delimiter in arguments")
        sys.exit(1)

    if len(args) < 4:
        print("Error: Missing required arguments for PROCESS_FOLDER, DISPLAY_FOLDER, TASK_ID and PROGRESS_json.")
        sys.exit(1)
    return args

if __name__ == "__main__":
    args = validate_args()
    PROCESS_FOLDER = args[0]
    GLB_FOLDER = args[1]
    TASK_ID = args[2]
    PROGRESS_json = args[3]
    print(f"PROGRESS_json: {PROGRESS_json}")
    
    try:
        INIT_PROGRESS = json.loads(PROGRESS_json)
    except json.JSONDecodeError as e:
        print(f"Failed to load progress JSON: {e}")
        INIT_PROGRESS = {}
    
    processed = []
    report_progress(TASK_ID, status="Blender Listener started", state="Started")
    
    print("Starting Blender Service... Watching for new files")
    while True:
        process_new_files()
        time.sleep(2)