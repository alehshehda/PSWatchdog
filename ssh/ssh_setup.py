import os
import subprocess

import getpass

# Get the current username
username = getpass.getuser()

# IP of the remote host
remote_host_ip = "192.168.0.100"

# Path to the .ssh directory in the user's home folder
ssh_dir = os.path.join(os.getenv('USERPROFILE'), '.ssh')

# Ensure the .ssh directory exists
if not os.path.exists(ssh_dir):
    os.makedirs(ssh_dir)

# Set key filename with username
ssh_key_path = os.path.join(ssh_dir, f'id_rsa_{username}')

# Ask for a passphrase (optional)
passphrase = input("Enter passphrase for the key (leave empty for none): ")

# Generate SSH key
command = ["ssh-keygen", "-t", "rsa", "-b", "2048", "-f", ssh_key_path, "-N", passphrase]

try:
    subprocess.run(command, check=True)
    print(f"Keys generated:\n Private Key: {ssh_key_path}\n Public Key: {ssh_key_path}.pub")
except subprocess.CalledProcessError as e:
    print(f"Error generating SSH key: {e}")

# Modify SSH config file to include the new host entry
config_file_path = os.path.join(ssh_dir, 'config')

# Create or append to the SSH config file
with open(config_file_path, 'a') as config_file:
    config_file.write(f"\nHost {remote_host_ip}\n")
    config_file.write(f"    User logsink\n")
    config_file.write(f"    IdentityFile {ssh_key_path}\n")

print(f"SSH config updated. New entry added for Host {remote_host_ip}.")
