import paramiko
import os
import json
import getpass
import time

# Get system username dynamically
USERNAME = getpass.getuser()

# Constant path to logs directory
LOCAL_LOGS_DIR = f"C:/Users/{USERNAME}/AppData/Local/PSWatchdog/monitoring/logs"

# SFTP Configuration
HOST = "192.168.0.100"
PORT = 22
SFTP_USERNAME = "logsink"
PRIVATE_KEY_PATH = f"C:/Users/{USERNAME}/.ssh/id_rsa_{USERNAME}"
REMOTE_BASE_DIR = "PSWatchdog"
UPLOADED_FILES_TRACKER = f"C:/Users/{USERNAME}/AppData/Local/PSWatchdog/monitoring/uploaded_files.json"


def load_uploaded_files():
    """Loads the list of previously uploaded files."""
    if os.path.exists(UPLOADED_FILES_TRACKER):
        with open(UPLOADED_FILES_TRACKER, "r") as f:
            return set(json.load(f))
    return set()


def save_uploaded_files(files):
    """Saves the list of uploaded files."""
    with open(UPLOADED_FILES_TRACKER, "w") as f:
        json.dump(list(files), f)


def get_files_to_upload():
    """Retrieves a list of files to upload, only M_ and H_ prefixed files."""
    uploaded_files = load_uploaded_files()

    # Select only files starting with M_ or H_
    all_files = {f for f in os.listdir(LOCAL_LOGS_DIR) if f.startswith(("M_", "H_"))}

    # Filter out already uploaded files
    new_files = all_files - uploaded_files

    return [os.path.join(LOCAL_LOGS_DIR, f) for f in new_files], new_files


def upload_files(files_to_upload, filenames):
    """Uploads new files to the SFTP server."""
    if not files_to_upload:
        print("No new files to upload.")
        return

    # Check if the SSH key exists
    if not os.path.exists(PRIVATE_KEY_PATH):
        print("Error: Private key does not exist!")
        return

    private_key = paramiko.RSAKey(filename=PRIVATE_KEY_PATH)

    # Establish SFTP connection
    transport = paramiko.Transport((HOST, PORT))
    transport.connect(username=SFTP_USERNAME, pkey=private_key)
    sftp = paramiko.SFTPClient.from_transport(transport)

    user_dir = f"{REMOTE_BASE_DIR}/{USERNAME}"

    # Create directory on server if it does not exist
    try:
        sftp.stat(user_dir)
    except FileNotFoundError:
        sftp.mkdir(user_dir)

    # Upload files
    for file in files_to_upload:
        remote_file_path = f"{user_dir}/{os.path.basename(file)}"
        sftp.put(file, remote_file_path)
        print(f"File {file} uploaded to {remote_file_path}")

    sftp.close()
    transport.close()

    # Save uploaded files to tracker
    uploaded_files = load_uploaded_files()
    uploaded_files.update(filenames)
    save_uploaded_files(uploaded_files)
    print("All new files have been uploaded.")


def upload_files_periodically():
    """Function to upload files every 30 seconds."""
    while True:
        files, filenames = get_files_to_upload()
        upload_files(files, filenames)
        time.sleep(30)  # Wait for 30 seconds before next upload
