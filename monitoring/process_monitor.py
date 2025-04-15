import psutil
import time
import logging
from log_generator import generate_log

# Configure basic logging to output messages with level INFO or higher.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def match_sigma_conditions(condition_dict, cmdline_lower):
    """
    Handles Sigma-style condition blocks.
    Returns True if any pattern is found in the command line.
    """
    # Ensure the condition is a dictionary.
    if not isinstance(condition_dict, dict):
        return False
    # Iterate over the condition dictionary items.
    for key, values in condition_dict.items():
        # Normalize the values to a list.
        values = values if isinstance(values, list) else [values]
        # Check for the '|contains' marker in the key and if any value matches.
        if "|contains" in key:
            if any(val.lower() in cmdline_lower for val in values):
                # Return True as soon as a matching pattern is found.
                return True
    # If no matching pattern is found, return False.
    return False


def check_rule_conditions(rule, proc):
    """
    Evaluates whether a process meets the Sigma rule conditions.
    The process must match selection conditions and NOT match any filter conditions.
    """
    # Retrieve detection settings from the rule; use an empty dict if not provided.
    detection = rule.get("detection", {})

    # Get the process command line as a list; join it to form a single string.
    cmdline_list = proc.info.get("cmdline", [])
    cmdline = " ".join(cmdline_list) if cmdline_list else ""
    # Convert the command line to lowercase for case-insensitive matching.
    cmdline_lower = cmdline.lower()

    # Extract the selection criteria from the detection block.
    selection = detection.get("selection")
    # If no selection is provided or there is no match, return False.
    if not selection or not match_sigma_conditions(selection, cmdline_lower):
        return False

    # Check filter conditions: if any filter matches, the process should be excluded.
    for key, value in detection.items():
        if key.startswith("filter_") and match_sigma_conditions(value, cmdline_lower):
            return False

    # Process passes selection and does not match any filter conditions.
    return True


def monitor_system(rules, stop_event):
    """
    Continuously monitors processes (e.g., Powershell) against Sigma rules.
    Checks the stop_event periodically and exits gracefully.
    """
    logger.info("Starting process monitoring...")
    try:
        # Main loop: runs until a stop event is set.
        while not stop_event.is_set():
            # Iterate through processes with required attributes.
            for proc in psutil.process_iter(["pid", "name", "cmdline"]):
                try:
                    # Get the process name in lowercase for consistent comparison.
                    process_name = proc.info.get("name", "").lower()
                    # Filter to monitor only processes related to "powershell".
                    if "powershell" not in process_name:
                        continue

                    # Retrieve the command line of the process.
                    cmdline = proc.info.get("cmdline", [])
                    # Skip processes without sufficient command line arguments.
                    if len(cmdline) <= 1:
                        continue

                    # Iterate through the set of Sigma rules to check for matches.
                    for rule in rules:
                        if check_rule_conditions(rule, proc):
                            # Generate a log entry if the process matches the rule conditions.
                            generate_log(rule, proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                    # Log specific process-related exceptions at debug level and continue.
                    logger.debug("Process exception: %s", e)
                    continue

            # Sleep for a total of 1 second, broken into short 0.1-second intervals,
            # to more frequently check if stop_event is set.
            for _ in range(10):
                if stop_event.is_set():
                    break
                time.sleep(0.1)
    except Exception as e:
        # Log any unexpected exceptions, including traceback information.
        logger.error("Exception in monitor_system: %s", e, exc_info=True)
    logger.info("monitor_system() exiting gracefully due to stop_event.")
