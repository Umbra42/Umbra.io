import os, time, sys, socketio, subprocess, argparse, functools, builtins, traceback, engineio
from pathlib import Path

print = functools.partial(builtins.print, flush=True)

PROGRESS = {
    "task_id": "",
    "state": "",
    "status": "", 
    "current_file_name": "",
    "total_file_n": "",
    "step_n": 0,
    "processed": {},  
}

processed = set()


def parse_args():
    global BLENDER_EXE, PROCESS_FOLDER, GLB_FOLDER, SERVER_URL
    parser = argparse.ArgumentParser()
    parser.add_argument("--blender_exe", type=str, required=True)
    parser.add_argument("--process_folder", type=str, required=True)
    parser.add_argument("--glb_folder", type=str, required=True)
    parser.add_argument("--server_url", type=str, default="http://127.0.0.1:5000")
    args = parser.parse_args()
    BLENDER_EXE = args.blender_exe
    PROCESS_FOLDER = args.process_folder
    GLB_FOLDER = args.glb_folder
    SERVER_URL = args.server_url

def connect_socetio():
    global sio
    sio = socketio.Client(logger=True, engineio_logger=True)
    try:
        print(f"Connecting to server at {SERVER_URL} ...", flush=True)
        sio.connect(SERVER_URL, namespaces=["/upload"], socketio_path="/socket.io", wait=True, wait_timeout=30)
        print("Connected to server")
    except Exception as e:
        print(f"Failed to connect to server: {e}")
        traceback.print_exc()
        sys.exit(1)

def convert_file(blend_path, glb_path):
    cmd = [
        BLENDER_EXE,
        "--background",
        "--python-expr",
        (
            f"import bpy; bpy.ops.wm.open_mainfile(filepath=r'{blend_path}'); bpy.ops.export_scene.gltf(filepath=r'{glb_path}', export_format='GLB')"
        )
    ]
    subprocess.run(cmd, check=True)  

def process_new_files(PROCESS_FOLDER, GLB_FOLDER):
    for filename in os.listdir(PROCESS_FOLDER):
        if not filename.lower().endswith(".blend") or filename in processed:
            
            continue

        blend_path = os.path.join(PROCESS_FOLDER, filename)
        glb_name = Path(filename).with_suffix(".glb").name
        glb_output = os.path.join(GLB_FOLDER, glb_name)
        emit_progress(status=f"Converting {filename}...", current_file_name=filename, state="Converting")
        print(f"Processing: \n     {blend_path} \n      ->      \n     {glb_output}")

        try:
            convert_file(blend_path, glb_output)
            print(f"Successfully converted: {blend_path}")
            # maybe add backup of the blend file to a different location
            os.remove(blend_path)  
            print(f"Removed: {blend_path}")
            
            entry = {
                "file_obj": blend_path,
                "glb_path": glb_output,
                "file_name": glb_name,
                "file_type": ".glb",
            }
            PROGRESS["processed"][filename] = entry
            processed.add(filename)
        except Exception as e:
            print(f"Failed to process {blend_path}: {e}")
    sio.emit("converted", PROGRESS, namespace="/upload")

    
def emit_progress(**fields):
    fields.setdefault("task_id", PROGRESS["task_id"])
    PROGRESS.update(fields)
    sio.emit("progress_update", PROGRESS, namespace="/upload")

    
''' TODO:
def track_step(task_id, current_file_name, step_n, total_steps, status):
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    step = { "step" : step_n, "status" : status, "time" : now }
    tracker = PROGRESS.get(task_id, {})
    if tracker and current_file_name in tracker["files"]:`
        tracker["files"][current_file_name].append(step)
'''

def listener_loop():
    print("Listener started...")
    print(f"Listener started with: \n BLENDER_EXE = {BLENDER_EXE} \n PROCESS_FOLDER= {PROCESS_FOLDER} \n GLB_FOLDER= {GLB_FOLDER}")    
    
    while True:
        response = sio.call("get_task", namespace="/upload", timeout=10)    
        task_id = response.get("task_id")
        if not task_id:
            print("No task found, waiting for new tasks...")
            time.sleep(1)
            continue
        
        PROGRESS["task_id"] = task_id
        PROGRESS.update(response.get("progress", {}))
        emit_progress(status="started processing", state="Started", task_id=task_id)
        process_new_files(PROCESS_FOLDER, GLB_FOLDER)

if __name__ == "__main__":
    parse_args()
    connect_socetio()
    listener_loop()