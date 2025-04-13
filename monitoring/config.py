import os
import json
import ipaddress

CONFIG_FILE = "server_config.json"


def is_valid_ip(ip):
    """
    Check if the provided string is a valid IPv4 or IPv6 address.
    """
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def get_server_ip():
    """
    Retrieve the server IP address from the JSON configuration file.
    If the file does not exist or does not contain a valid IP address,
    prompt the user for a valid IP, save it to the file, and return it.
    """
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
                ip = data.get("server_ip")
                if ip and is_valid_ip(ip):
                    # Return the valid IP if found in the configuration file.
                    return ip
                else:
                    print("Invalid or missing IP address in configuration.")
        except Exception as e:
            print("Error reading configuration file:", e)

    # Prompt the user until a valid IP address is provided.
    while True:
        ip = input("Enter the server IP address: ")
        if is_valid_ip(ip):
            break
        print("Invalid IP address provided. Please enter a valid IP address.")

    # Save the valid IP address into the configuration file.
    data = {"server_ip": ip}
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print("Error writing configuration file:", e)

    return ip
