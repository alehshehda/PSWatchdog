import psutil
import time
from log_generator import generate_log


def match_condition(condition, cmdline):
    """Checks if the command matches the rule conditions."""
    if isinstance(condition, dict):
        for key, value in condition.items():
            if "|contains" in key:
                if any(val in cmdline for val in (value if isinstance(value, list) else [value])):
                    return True
    return False


def check_rule_conditions(rule, proc):
    """Checks if a process meets the rule conditions."""
    detection = rule.get("detection", {})
    cmdline = " ".join(proc.info.get("cmdline", [])) if proc.info.get("cmdline") else ""

    if "selection" in detection:
        if not match_condition(detection["selection"], cmdline):
            return False

    for key, condition in detection.items():
        if key.startswith("filter_") and match_condition(condition, cmdline):
            return False

    return True


def monitor_system(rules):
    """Monitors processes and checks them against preloaded SIGMA rules."""
    print("Starting PowerShell process monitoring...")

    while True:
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                if "powershell" in proc.info["name"].lower():
                    cmdline = proc.info.get("cmdline", [])

                    # Ignore "powershell.exe" without arguments
                    if len(cmdline) <= 1:
                        continue

                    for rule in rules:
                        if check_rule_conditions(rule, proc):
                            generate_log(rule, proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        time.sleep(1)  # Prevents excessive CPU usage
