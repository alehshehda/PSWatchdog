import os
import yaml
import pickle
import tempfile
import logging

# Set up basic logging to output messages with level INFO or above.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the base directory where this script is located.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Define the directory that contains the YAML rule files.
RULES_DIR = os.path.join(BASE_DIR, "rules")
# Define the cache file path for storing the loaded rules.
CACHE_FILE = os.path.join(BASE_DIR, "rules_cache.pkl")

def get_latest_mod_time(directory):
    """
    Returns the latest modification time among all YAML files in the given directory.
    This is used to determine if any rules have been updated.
    """
    latest_time = 0
    # Walk through the directory recursively.
    for root, _, files in os.walk(directory):
        for filename in files:
            # Consider only YAML files (with .yml or .yaml extension).
            if filename.endswith((".yml", ".yaml")):
                filepath = os.path.join(root, filename)
                # Update the latest_time if this file has been modified more recently.
                latest_time = max(latest_time, os.path.getmtime(filepath))
    return latest_time

def save_cache(data, cache_file):
    """
    Safely saves the cache data to the specified cache file using a temporary file.
    This prevents partial writes that might corrupt the cache.
    """
    temp_dir = os.path.dirname(cache_file)
    # Create a temporary file in the same directory.
    with tempfile.NamedTemporaryFile("wb", delete=False, dir=temp_dir) as tmp_file:
        pickle.dump(data, tmp_file)
        temp_name = tmp_file.name
    # Replace the existing cache file with the temporary file atomically.
    os.replace(temp_name, cache_file)

def load_rules():
    """
    Loads YAML rules using a caching mechanism.
    If no YAML file has changed since the last load, the rules are loaded from a cache file.
    Otherwise, the rules are reloaded from the YAML files and the cache is updated.
    """
    latest_mod_time = get_latest_mod_time(RULES_DIR)

    # Check if a valid, up-to-date cache exists.
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "rb") as f:
                cache_data = pickle.load(f)
                # If the modification time in the cache matches the latest, return cached rules.
                if cache_data.get("mod_time") == latest_mod_time:
                    logger.info("Loaded rules from cache")
                    return cache_data.get("rules", [])
        except (pickle.UnpicklingError, EOFError) as e:
            # If cache is corrupted or unreadable, log a warning and proceed to reload rules.
            logger.warning("Cache file corrupted, reloading rules from YAML: %s", e)

    # Otherwise, load rules from all YAML files in the directory.
    rules = []
    for root, _, files in os.walk(RULES_DIR):
        for filename in files:
            if filename.endswith((".yml", ".yaml")):
                filepath = os.path.join(root, filename)
                try:
                    # Load each YAML file safely.
                    with open(filepath, "r", encoding="utf-8") as file:
                        rule = yaml.safe_load(file)
                        if rule is not None:
                            rules.append(rule)
                except yaml.YAMLError as e:
                    logger.error("Error loading YAML file: %s - %s", filepath, e)

    # Build cache data with the loaded rules and latest modification time.
    cache_data = {"rules": rules, "mod_time": latest_mod_time}
    # Save the new cache data safely.
    save_cache(cache_data, CACHE_FILE)
    logger.info("Loaded %d rules (fresh load)", len(rules))
    return rules
