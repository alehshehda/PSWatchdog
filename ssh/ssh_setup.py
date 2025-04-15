import os
import subprocess
import getpass
import ipaddress
import platform
import sys
import logging

# Set up basic logging to output simple messages.
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

def is_valid_ip(ip):
    """
    Check if the provided IP address is valid.
    Returns True if valid, otherwise returns False.
    """
    try:
        # Use ipaddress module to validate the IP.
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def set_hidden_windows(path):
    """
    Mark the specified folder as hidden in Windows.
    This function runs only if the operating system is Windows.
    """
    if platform.system() == "Windows":
        try:
            # Run the attrib command to add the hidden attribute to the folder.
            subprocess.run(["attrib", "+h", path], shell=True, check=True)
            logger.info(f"Folder {path} has been marked as hidden.")
        except subprocess.CalledProcessError:
            logger.warning(f"Could not hide {path}. You can ignore this if on non-Windows.")

def get_ssh_dir():
    """
    Return the user's SSH directory.
    Create it if it does not exist and mark it as hidden on Windows.
    """
    home_dir = os.path.expanduser("~")
    ssh_path = os.path.join(home_dir, ".ssh")
    # Create the .ssh directory if it doesn't exist.
    if not os.path.exists(ssh_path):
        os.makedirs(ssh_path)
        set_hidden_windows(ssh_path)
    return ssh_path

def generate_ssh_key(key_path, passphrase):
    """
    Generate a new SSH key if one does not already exist at the given path.
    Uses RSA algorithm with a 2048-bit key size.
    """
    if os.path.exists(key_path):
        logger.info(f"Key already exists at: {key_path}. Skipping generation.")
        return

    # Prepare the ssh-keygen command with provided key path and passphrase.
    command = ["ssh-keygen", "-t", "rsa", "-b", "2048", "-f", key_path, "-N", passphrase]
    try:
        subprocess.run(command, check=True)
        logger.info(f"SSH key generated:\n  Private key: {key_path}\n  Public key: {key_path}.pub")
    except subprocess.CalledProcessError as e:
        logger.error(f"SSH key generation failed: {e}")
        sys.exit(1)

def update_ssh_config(config_path, host_alias, server_ip, ssh_username, identity_file):
    """
    Append an SSH configuration entry for the remote server.
    If an entry for the server IP already exists, it will be skipped.
    """
    # Build the configuration entry for the remote server.
    config_entry = (
        f"\nHost {server_ip}\n"
        f"    User {ssh_username}\n"
        f"    IdentityFile {identity_file}\n"
    )

    # Check if the SSH config already contains an entry for the server IP.
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            if f"Host {server_ip}" in f.read():
                logger.info(f"SSH config already contains an entry for '{server_ip}'. Skipping.")
                return

    # Append the new configuration entry to the SSH config file.
    with open(config_path, "a") as f:
        f.write(config_entry)
    logger.info(f"SSH config updated with entry for '{server_ip}'.")

def main():
    """
    Main function to run the SSH key generation and configuration update process.
    Prompts the user for necessary input and executes the sequence of operations.
    """
    logger.info("SSH Key Setup for Remote Connection\n")

    # Prompt the user for a valid remote server IP address.
    while True:
        server_ip = input("Enter remote server IP address: ").strip()
        if is_valid_ip(server_ip):
            break
        logger.warning("Invalid IP. Please try again.")

    # Prompt the user for the SSH username.
    ssh_username = input("Enter SSH username for remote server: ").strip()
    if not ssh_username:
        logger.error("SSH username cannot be empty.")
        sys.exit(1)

    # Get the user's SSH directory and define the key file path.
    ssh_dir = get_ssh_dir()
    local_username = getpass.getuser()
    key_filename = f"id_rsa_{local_username}"
    key_path = os.path.join(ssh_dir, key_filename)

    # Prompt the user for a passphrase for the SSH key (optional).
    passphrase = input("Enter passphrase for key (leave empty for none): ")

    # Define the path for the SSH configuration file.
    config_path = os.path.join(ssh_dir, "config")

    # Generate the SSH key and update the SSH configuration.
    generate_ssh_key(key_path, passphrase)
    update_ssh_config(config_path, server_ip, server_ip, ssh_username, key_path)

    logger.info("\nSSH key setup complete.")
    logger.info(f"You can now connect using: ssh {server_ip}")

if __name__ == "__main__":
    main()
