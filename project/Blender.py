import os
import urllib
import zipfile
import subprocess

from helpers import apology
from upload import is_unique

def make_blender(system):
    if system == "Windows":
        blender_path = "Blender"
        url = "https://ftp.nluug.nl/pub/graphics/blender/release/Blender4.1/blender-4.1.0-windows-x64.zip"        
    elif system == "Linux":
        blender_path = "/usr/bin/blender/blender"
        url = "https://ftp.nluug.nl/pub/graphics/blender/release/Blender4.1/blender-4.1.0-linux-x64.tar.xz"
            
    full_blender_path = os.path.join(os.getcwd(), 'apps', blender_path)
    print(f"blender instance path: {full_blender_path}")
    if not blender_exists(full_blender_path):
        download_path = os.path.join(os.getcwd(), 'apps')
        install_blender(url, download_path, full_blender_path, system)

        return full_blender_path
    
def blender_exists(path):
    if os.path.exists(path):
        print("blender found")
        return True
    print("could not find blender")
    return False

def install_blender(url, download_path, full_blender_path, system):
    print("checking system")
    match system:
        case "Windows":
            print("downloading zip")
            zip_path = download_blender(url, download_path)
            extract_to(zip_path, full_blender_path)
            return(zip_path)
        case "linux":
            # add method for linux
            print("method to be added")
            ... 

def download_blender(url, download_path):
    file_name = url.rstrip('/').split('/')[-1]
    zip_path = os.path.join(download_path, file_name)

    req = urllib.request.Request(
        url,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
    )
    with urllib.request.urlopen(req) as response, open(zip_path, 'wb') as out_file:
        data = response.read()
        out_file.write(data)
    
    return zip_path

def extract_to(zip_path, full_blender_path):
    # Extract the downloaded file
    print(f"extracting from {zip_path} to {full_blender_path}")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(full_blender_path)
        print(f"install complete: {zip_path}")
        try:
            os.remove(zip_path)
            print(f"File {zip_path} has been removed successfully")
        except FileNotFoundError:
            print("The file does not exist")
        except PermissionError:
            print("You do not have permissions to delete the file")
        except Exception as e:
            print(f"Error occurred: {e}")
    except zipfile.BadZipFile:
        apology("not a valid zip", 304)

def run_conversion(input, output, path):
    print(f"inputpath: {input}", '\n',f"outputpath: {output}", '\n', path)
    script_path = os.path.join(os.getcwd(), 'scripts', 'convert.py')
    command = [ 
        path,
        '--background', 
        '--python', script_path,
        '--',
        input,
        output,
    ]
    if os.access(output, os.W_OK):
        try:
            subprocess.run(command, check=True)
            print("Conversion successful.")
        except subprocess.CalledProcessError as e:
            print(f"Blender script failed with return code: {e.returncode}")
        except PermissionError:
            print(f"You do not have permissions to save the converted file here: {output}")
        except Exception as e:
            print(f"An error occurred: {e}")
    else:
    # Directory does not exist or is not writable
        print("Directory does not exist or is not writable")  




