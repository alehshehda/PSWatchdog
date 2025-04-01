import os
import json
from datetime import datetime
import getpass

# Get the script's base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

USERNAME = getpass.getuser()

def generate_log(rule, proc):
    """Creates and saves a log of detected threats, including the executed command"""
    current_time = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    level_map = {"low": "L", "medium": "M", "high": "H"}
    level = level_map.get(rule.get("level", "medium"), "M")  
    attack_type = rule.get("title", "Unknown").replace(" ", "_")

    log_filename = f"{level}_{current_time}_{USERNAME}_{attack_type}.log"
    log_path = os.path.join(LOG_DIR, log_filename)

    # Retrieve the full command that launched the process
    cmdline = " ".join(proc.info.get("cmdline", [])) if proc.info.get("cmdline") else "N/A"

    log_entry = {
        "timestamp": current_time,
        "user": USERNAME,
        "process": proc.info.get("name", "Unknown"),
        "cmdline": cmdline,
        "rule": {
            "title": rule.get("title", "Unknown"),
            "id": rule.get("id", "Unknown"),
            "description": rule.get("description", "No description available"),
            "level": rule.get("level", "medium"),
            "tags": rule.get("tags", []),
            "references": rule.get("references", [])
        }
    }

    with open(log_path, "w", encoding="utf-8") as log_file:
        json.dump(log_entry, log_file, indent=4)

    print(f"Threat detected! Log saved: {log_filename}")
