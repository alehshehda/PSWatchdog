import os
import json
import logging
from logging.handlers import RotatingFileHandler
import getpass
from datetime import datetime
import base64

# Set up the base directory and the logs folder.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Get the current username and define the shared log file path.
USERNAME = getpass.getuser()
SHARED_LOG_FILE = os.path.join(LOG_DIR, "threats.log")


def setup_logger():
    """
    Sets up a rotating file logger that writes threat logs in JSON format.
    Log file rotates when it reaches 5MB, keeping 5 backups.
    Ensures only one handler is attached to avoid duplicate logs.
    """
    logger = logging.getLogger("ThreatLogger")
    logger.setLevel(logging.INFO)

    # Only configure the logger once.
    if not getattr(logger, "_is_configured", False):
        # Create a file handler with rotation to manage large log files.
        handler = RotatingFileHandler(
            SHARED_LOG_FILE,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=5,
            encoding="utf-8"
        )
        # Define a simple formatter that outputs only the message (JSON string).
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # Prevent the log messages from being passed to the root logger.
        logger.propagate = False
        logger._is_configured = True

    return logger


# Initialize logger.
logger = setup_logger()


def extract_executed_code(cmdline_parts):
    """
    Extracts the actual executed PowerShell code from command-line arguments.
    Handles different cases:
      - "-Command": Inline PowerShell code provided directly.
      - "-EncodedCommand": Base64 encoded Unicode command which is decoded.
      - "-File": A script file is specified; its contents are read from disk.
    Returns a string with the executed code or an error message if extraction fails.
    """
    if not cmdline_parts:
        return "N/A"

    try:
        if "-Command" in cmdline_parts:
            idx = cmdline_parts.index("-Command")
            # Concatenate all parts after "-Command" as the inline command.
            return " ".join(cmdline_parts[idx + 1:])
        elif "-EncodedCommand" in cmdline_parts:
            idx = cmdline_parts.index("-EncodedCommand")
            encoded = cmdline_parts[idx + 1]
            try:
                # Decode the Base64 string and then decode it from UTF-16LE to get the original code.
                decoded = base64.b64decode(encoded).decode("utf-16le")
                return decoded
            except Exception as e:
                logger.exception("Failed to decode encoded command")
                return f"[Failed to decode encoded command: {str(e)}]"
        elif "-File" in cmdline_parts:
            idx = cmdline_parts.index("-File")
            script_path = cmdline_parts[idx + 1]
            if os.path.isfile(script_path):
                try:
                    with open(script_path, "r", encoding="utf-8", errors="ignore") as f:
                        return f.read()
                except Exception as e:
                    logger.exception("Error reading script file")
                    return f"[Error reading script file: {script_path} - {str(e)}]"
            else:
                return f"[Script file not found: {script_path}]"
    except Exception as e:
        logger.exception("Failed to extract executed code from cmdline")
        return f"[Failed to extract executed code: {str(e)}]"

    return "N/A"


def generate_log(rule, proc):
    """
    Creates a JSON-formatted threat log entry and writes it to the shared log file.
    The log includes:
      - Timestamp in ISO 8601 format.
      - User information.
      - Process details such as process name, PID, and full command-line.
      - The extracted executed PowerShell code.
      - Information about the matching rule.
    """
    # Get the current timestamp in ISO 8601 format.
    current_time = datetime.now().isoformat()

    # Extract command-line parts from the process info.
    cmdline_parts = proc.info.get("cmdline", [])
    cmdline_str = " ".join(cmdline_parts) if cmdline_parts else "N/A"
    # Extract the actual code executed via PowerShell from the command-line.
    executed_code = extract_executed_code(cmdline_parts)

    # Build the log entry as a dictionary.
    log_entry = {
        "timestamp": current_time,
        "user": USERNAME,
        "process": proc.info.get("name", "Unknown"),
        "pid": proc.info.get("pid", "Unknown"),
        "cmdline": cmdline_str,
        "executed_code": executed_code,
        "rule": {
            "title": rule.get("title", "Unknown"),
            "id": rule.get("id", "Unknown"),
            "description": rule.get("description", "No description available"),
            "level": rule.get("level", "medium"),
            "tags": rule.get("tags", []),
            "references": rule.get("references", [])
        }
    }

    # Write the JSON-formatted log entry to the shared log file.
    try:
        logger.info(json.dumps(log_entry))
        print(f"Threat detected! Log entry created at {current_time}")
    except Exception as e:
        logger.exception("Failed to write log entry")
