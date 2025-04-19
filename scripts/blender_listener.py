import bpy
import json
import os
import time
import sys
import socketio

sio = socketio.Client()
PROGRESS = {}
processed = []

def validate_args():  
    if "--" in sys.argv:
        args = sys.argv[sys.argv.index("--") + 1:]
        print(f"[BLENDER SCRIPT] ARGS: {args}")
    else:
        print("[BLENDER SCRIPT] Error: Missing '--' delimiter in arguments")
        sys.exit(1)

    if len(args) < 4:
        print("[BLENDER_SCRIPT] Error: Missing required arguments for either: PROCESS_FOLDER, DISPLAY_FOLDER, TASK_ID and PROGRESS_json.")
        sys.exit(1)
    return args
  
def process_new_files(PROCESS_FOLDER, GLB_FOLDER, TASK_ID):
    for filename in os.listdir(PROCESS_FOLDER):
        if filename.endswith(".blend") or filename in processed:
            continue

        blend_path = os.path.join(PROCESS_FOLDER, filename)
        glb_name = filename.replace(".blend", ".glb")
        glb_output = os.path.join(GLB_FOLDER, glb_name)
        emit_progress(status=f"Converting {filename}...", current_file_name=filename, state="Converting")
        print(f"[BLENDER SCRIPT] Processing: \n     {blend_path} \n      ->      \n     {glb_output}")

        try:
            bpy.ops.wm.open_mainfile(filepath=blend_path)
            bpy.ops.export_scene.gltf(filepath=glb_output, export_format='GLB')
            emit_progress(status=f"Converted {filename}", current_file_name=glb_name, state="Done")
            print(f"[BLENDER SCRIPT]Successfully converted: {blend_path}")
            processed.append(filename)
            # maybe add backup of the blend file to a different location
            os.remove(blend_path)  
        except Exception as e:
            print(f"[BLENDER SCRIPT] Failed to process {blend_path}: {e}")

def emit_progress(**fields):
    PROGRESS.update(fields)
    payload = PROGRESS.copy()
    
    if "current_file_name" in fields:
        current_file = fields["current_file_name"]
        PROGRESS.setdefault("files", {}).setdefault(current_file, []).append({
            "step": fields.get("step_n"),
            "status": fields.get("status"),
            "time": time.strftime("%Y-%m-%d %H:%M:%S")
        })

        payload["files"] = PROGRESS["files"][current_file]
        print(f"[BLENDER SCRIPT] payload", payload)

    try:
        sio.emit("progress_update", payload, namespace="/upload")   
    except Exception as e:
        print(f"[BLENDER SCRIPT] Failed to report progress: {e}")
        import traceback
        traceback.print_exc()
    
''' TODO:
def track_step(task_id, current_file_name, step_n, total_steps, status):
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    step = { "step" : step_n, "status" : status, "time" : now }
    tracker = PROGRESS.get(task_id, {})
    if tracker and current_file_name in tracker["files"]:
        tracker["files"][current_file_name].append(step)
'''

def main():
    print("[BLENDER SCRIPT] Listener started...")
    PROCESS_FOLDER, GLB_FOLDER, TASK_ID, PROGRESS_json = validate_args()
    PROGRESS.update(json.loads(PROGRESS_json))
    print(f"[BLENDER SCRIPT] Listener started with: PROCESS_FOLDER= {PROCESS_FOLDER} \n GLB_FOLDER= {GLB_FOLDER} \n TASK_ID= {TASK_ID} \n json= {PROGRESS}")    

    sio.connect("http://127.0.0.1:5000", namespaces=["/progress"])
    emit_progress(status="Blender Listener started", state="Started")
    while True:                  
        process_new_files(PROCESS_FOLDER, GLB_FOLDER)
        time.sleep(1)

if __name__ == "__main__":
    main()