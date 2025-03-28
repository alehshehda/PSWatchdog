import os
import sys
import getpass
from sftp_uploader import upload_files  # Import function from main script

# Configuration
USER = getpass.getuser()
FILES_DIR = f"C:/Users/{USER}/Desktop/logs"  # Directory with files to upload

# Get all files from the directory
if not os.path.exists(FILES_DIR):
    print(f"Error: Directory {FILES_DIR} does not exist!")
    sys.exit(1)

files = [os.path.join(FILES_DIR, f) for f in os.listdir(FILES_DIR) if os.path.isfile(os.path.join(FILES_DIR, f))]

if not files:
    print("No files to upload.")
    sys.exit(0)

# Call the upload function
upload_files(files)
