import os
import json
import ipaddress
import logging

# Configure logging to display messages with INFO level or higher.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the base directory as the directory where this script is located.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Configuration directory and file; here we use the same directory as BASE_DIR.
CONFIG_DIR = BASE_DIR
CONFIG_FILE = os.path.join(CONFIG_DIR, "server_config.json")

# Ensure that the configuration directory exists.
os.makedirs(CONFIG_DIR, exist_ok=True)


def is_valid_ip(ip):
    """
    Checks if the provided string is a valid IP address.
    Returns True if valid, otherwise returns False.
    """
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def load_config():
    """
    Loads the JSON configuration file.
    Returns the configuration as a dictionary if the file exists and is valid.
    Otherwise, returns an empty dictionary.
    """
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except (json.JSONDecodeError, IOError) as e:
            # Warn if there is an error reading the configuration file.
            logger.warning("Error reading configuration file: %s", e)
    return {}


def save_config(config):
    """
    Saves the configuration dictionary into the JSON configuration file.
    """
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as file:
            json.dump(config, file, indent=4)
    except IOError as e:
        # Log an error if the configuration file cannot be written.
        logger.error("Error writing configuration file: %s", e)


def get_server_ip_and_port():
    """
    Retrieves the server IP address and port from the JSON configuration file.
    If the file does not exist or does not contain valid values,
    prompts the user for valid values, saves them to the file, and returns them.
    """
    config = load_config()
    ip = config.get("server_ip")
    port = config.get("server_port")

    # Validate IP
    if not (ip and is_valid_ip(ip)):
        if ip:
            logger.info("Invalid IP address found in configuration: %s", ip)
        else:
            logger.info("Server IP not found in configuration.")
        while True:
            ip = input("Enter the server IP address: ")
            if is_valid_ip(ip):
                break
            print("Invalid IP address provided. Please enter a valid IP address.")
        config["server_ip"] = ip

    # Validate Port
    if not (port and str(port).isdigit() and 1 <= int(port) <= 65535):
        if port:
            logger.info("Invalid port found in configuration: %s", port)
        else:
            logger.info("Server port not found in configuration.")
        while True:
            port_input = input("Enter the server port (1-65535): ")
            if port_input.isdigit() and 1 <= int(port_input) <= 65535:
                port = int(port_input)
                break
            print("Invalid port. Please enter a number between 1 and 65535.")
        config["server_port"] = port

    save_config(config)
    return ip, int(port)
