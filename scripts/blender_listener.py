import bpy
import os
import time
import sys

if "--" in sys.argv:
    args = sys.argv[sys.argv.index("--") + 1:]
    if len(args) < 2:
        print("Error: Missing required arguments for PROCESS_FOLDER and DISPLAY_FOLDER.")
        sys.exit(1)
    
    WATCH_FOLDER = args[0]
    OUTPUT_FOLDER = args[1]
else:
    print("Error: No arguments received. Exiting.")
    sys.exit(1)

def process_new_files():
    """Check for new .blend files and convert them"""
    for filename in os.listdir(WATCH_FOLDER):
        if filename.endswith(".blend"):
            blend_path = os.path.join(WATCH_FOLDER, filename)
            glb_output = os.path.join(OUTPUT_FOLDER, filename.replace(".blend", ".glb"))

            print(f"Processing {blend_path} -> {glb_output}")

            try:
                bpy.ops.wm.open_mainfile(filepath=blend_path)
                bpy.ops.export_scene.gltf(filepath=glb_output, export_format='GLB')
                print(f"Successfully converted: {blend_path}")
                os.remove(blend_path)  # Cleanup processed files
            except Exception as e:
                print(f"Failed to process {blend_path}: {e}")

if __name__ == "__main__":
    print("Starting Blender Service... Watching for new files")
    while True:
        process_new_files()
        time.sleep(5)  # Check every 5 seconds