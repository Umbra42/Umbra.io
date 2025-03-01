import bpy
import sys
import os

def convert_blend_to_glb(blend_file_path, output_glb_path):
    """Convert a .blend file to .glb format"""
    try:
        print(f"Loading Blender file: {blend_file_path}")
        bpy.ops.wm.open_mainfile(filepath=blend_file_path)

        print(f"Exporting to GLB: {output_glb_path}")
        bpy.ops.export_scene.gltf(filepath=output_glb_path, export_format='GLB')

        print(f"Conversion complete: {blend_file_path} -> {output_glb_path}")
        return True
    except Exception as e:
        print(f"Error during conversion: {e}")
        return False

if __name__ == "__main__":
    # Get arguments from command line
    args = sys.argv[sys.argv.index("--") + 1:]

    if len(args) < 2 or len(args) % 2 != 0:
        print("Usage: blender --background --python convert.py -- <blend_file1> <glb_output1> [<blend_file2> <glb_output2> ...]")
        sys.exit(1)

    # Process files in pairs (blend_file -> glb_output)
    for i in range(0, len(args), 2):
        blend_file = args[i]
        glb_output = args[i + 1]

        if not os.path.exists(blend_file):
            print(f"Error: File {blend_file} does not exist")
            continue

        convert_blend_to_glb(blend_file, glb_output)