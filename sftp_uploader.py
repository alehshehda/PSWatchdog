import paramiko
import os
import getpass

def upload_files(files_to_upload):
    """
    Uploads files to an SFTP server.
    :param files_to_upload: list of file paths to be uploaded
    """
    if not files_to_upload:
        print("No files to upload.")
        return
    
    # Configuration
    USERNAME = getpass.getuser()  # Dynamically retrieve the current user
    HOST = "192.168.0.100"  # SFTP server address
    PORT = 22  # SSH port
    SFTP_USERNAME = "logsink"  # SFTP server user
    PRIVATE_KEY_PATH = "C:/Users/{}/.ssh/id_rsa_{}".format(USERNAME, USERNAME)
    REMOTE_BASE_DIR = "PSWatchdog"  # Adjusted for ChrootDirectory
    
    # Check if the private key exists
    if not os.path.exists(PRIVATE_KEY_PATH):
        print("Error: Private key does not exist!")
        return
    
    # Load private key
    private_key = paramiko.RSAKey(filename=PRIVATE_KEY_PATH)
    
    # Connect to SFTP server
    transport = paramiko.Transport((HOST, PORT))
    transport.connect(username=SFTP_USERNAME, pkey=private_key)
    sftp = paramiko.SFTPClient.from_transport(transport)
    
    # User directory path on the server
    user_dir = f"{REMOTE_BASE_DIR}/{USERNAME}"
    
    # Create remote directory recursively
    def ensure_remote_directory(sftp, path):
        try:
            sftp.stat(path)
        except FileNotFoundError:
            parent = os.path.dirname(path)
            if parent:
                ensure_remote_directory(sftp, parent)
            print(f"Creating directory: {path}")
            sftp.mkdir(path)
    
    ensure_remote_directory(sftp, user_dir)
    
    # Upload files one by one
    for file in files_to_upload:
        if os.path.exists(file):
            remote_file_path = f"{user_dir}/{os.path.basename(file)}"
            sftp.put(file, remote_file_path)
            print(f"File {file} has been uploaded to {remote_file_path}")
        else:
            print(f"File {file} does not exist, skipping.")
    
    # Close connection
    sftp.close()
    transport.close()
    print("All files have been uploaded.")
