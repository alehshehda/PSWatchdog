import os
import yaml
import getpass
import pickle

# Get the script's base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RULES_DIR = os.path.join(BASE_DIR, "rules")
CACHE_FILE = os.path.join(BASE_DIR, "rules_cache.pkl")

def get_latest_mod_time(directory):
    """Returns the latest modification time of any file in the directory."""
    latest_time = 0
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.endswith((".yml", ".yaml")):
                filepath = os.path.join(root, filename)
                latest_time = max(latest_time, os.path.getmtime(filepath))
    return latest_time

def load_rules():
    """Loads YAML rules with caching mechanism."""
    # If cache exists and is up to date, load from cache
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "rb") as f:
            try:
                cache_data = pickle.load(f)
                if cache_data["mod_time"] == get_latest_mod_time(RULES_DIR):
                    print("Loaded rules from cache")
                    return cache_data["rules"]
            except (pickle.UnpicklingError, EOFError):
                print("Cache file corrupted, reloading rules from YAML.")

    # Otherwise, load rules from YAML files
    rules = []
    for root, _, files in os.walk(RULES_DIR):
        for filename in files:
            if filename.endswith((".yml", ".yaml")):
                filepath = os.path.join(root, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as file:
                        rule = yaml.safe_load(file)
                        rules.append(rule)
                except yaml.YAMLError as e:
                    print(f"Error loading YAML file: {filepath} - {e}")

    # Save new cache
    with open(CACHE_FILE, "wb") as f:
        pickle.dump({"rules": rules, "mod_time": get_latest_mod_time(RULES_DIR)}, f)

    print(f"Loaded {len(rules)} rules (fresh load)")
    return rules
