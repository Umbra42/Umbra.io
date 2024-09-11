import bpy
import sys

# Set the path to the .blend file you want to convert and the output path for the .glb file
# These paths could be passed as arguments to the script
blend_file_path = sys.argv[sys.argv.index("--") + 1]
output_glb_path = sys.argv[sys.argv.index("--") + 2]

# Load the .blend file
bpy.ops.wm.open_mainfile(filepath=blend_file_path)

# Export the scene to GLB format
bpy.ops.export_scene.gltf(filepath=output_glb_path, export_format='GLB')

print(f"Conversion complete: {blend_file_path} -> {output_glb_path}")