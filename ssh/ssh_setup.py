import os
import subprocess
import getpass
import ipaddress

def is_valid_ip(ip):
    """
    Checks if the provided string is a valid IPv4 or IPv6 address.
    """
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

# Prompt the user for the remote host IP address until a valid address is provided
while True:
    server_ip = input("Enter the server IP address: ")
    if is_valid_ip(server_ip):
        break
    print("Invalid IP address, please try again.")

# Get the current username
username = getpass.getuser()

# Path to the .ssh directory in the user's home folder
ssh_dir = os.path.join(os.getenv('USERPROFILE'), '.ssh')

# Ensure the .ssh directory exists and set it as hidden (Windows specific)
if not os.path.exists(ssh_dir):
    os.makedirs(ssh_dir)
    # Set the folder as hidden on Windows
    try:
        subprocess.run(["attrib", "+h", ssh_dir], shell=True, check=True)
        print(f"Folder {ssh_dir} has been marked as hidden.")
    except subprocess.CalledProcessError:
        print(f"Error setting the hidden attribute for the folder {ssh_dir}.")

# Set key filename with username
ssh_key_path = os.path.join(ssh_dir, f'id_rsa_{username}')

# Ask for a passphrase (optional)
passphrase = input("Enter passphrase for the key (leave empty for none): ")

# Generate the SSH key
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
    config_file.write(f"\nHost {server_ip}\n")
    config_file.write("    User logsink\n")
    config_file.write(f"    IdentityFile {ssh_key_path}\n")

print(f"SSH config updated. New entry added for Host {server_ip}.")
