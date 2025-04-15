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


def get_server_ip():
    """
    Retrieves the server IP address from the JSON configuration file.
    If the file does not exist or does not contain a valid IP address,
    prompts the user for a valid IP, saves it to the file, and returns it.
    """
    # Load the existing configuration from the JSON file.
    config = load_config()
    ip = config.get("server_ip")

    # Check if a valid IP is already set in the configuration.
    if ip and is_valid_ip(ip):
        # Return the valid IP found in the configuration file.
        return ip
    else:
        if ip:
            # Inform the user if an invalid IP was found.
            logger.info("Invalid IP address found in configuration: %s", ip)
        else:
            # Inform the user that there is no IP configured.
            logger.info("Server IP not found in configuration.")

    # Continuously prompt the user until a valid IP address is provided.
    while True:
        ip = input("Enter the server IP address: ")
        if is_valid_ip(ip):
            break
        print("Invalid IP address provided. Please enter a valid IP address.")

    # Save the valid IP address into the configuration file.
    config["server_ip"] = ip
    save_config(config)

    return ip
