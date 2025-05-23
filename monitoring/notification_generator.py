import requests
import hashlib
import json
from dotenv import load_dotenv
import os


load_dotenv()  # Load variables from .env

TOKEN = os.getenv("TELEGRAM_TOKEN")
IDS = os.getenv("TELEGRAM_CHAT_IDS").split(",")
print(f"Chat IDs: {IDS}")
url_updates = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

response = requests.get(url_updates)
print(response.json())

# Store hashes of sent logs to avoid duplicates
_sent_log_hashes = set()
"""
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
"""

def send_notification(logs: dict, severity: str):
    # Remove 'timestamp' from logs before hashing
    logs_for_hash = dict(logs)  # shallow copy
    logs_for_hash.pop("timestamp", None)
    log_hash = hashlib.sha256(json.dumps(logs_for_hash, sort_keys=True).encode()).hexdigest()
    if log_hash in _sent_log_hashes:
        print("Duplicate threat detected, notification not sent.")
        return
    _sent_log_hashes.add(log_hash)

    # Send Telegram notification
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    for chat_id in IDS:
        # Format the log for better readability in Telegram
        rule = logs.get("rule", {})
        log_message = (
            f"<b>PSWatchdog Alert</b>\n"
            f"<b>Severity:</b> {severity}\n"
            f"<b>User:</b> {logs.get('user', 'Unknown')}\n"
            f"<b>Process:</b> {logs.get('process', 'Unknown')} (PID: {logs.get('pid', 'Unknown')})\n"
            f"<b>Cmdline:</b> {logs.get('cmdline', 'N/A')}\n"
            f"<b>Executed Code:</b> {logs.get('executed_code', 'N/A')}\n"
            f"<b>Rule:</b> {rule.get('title', 'Unknown')} (ID: {rule.get('id', 'Unknown')})\n"
            f"<b>Description:</b> {rule.get('description', 'No description available')}\n"
            f"<b>Tags:</b> {', '.join(rule.get('tags', []))}\n"
            f"<b>References:</b> {'; '.join(rule.get('references', []))}\n"
        )
        params = {
            "chat_id": chat_id,
            "text": log_message,
            "parse_mode": "HTML"
        }
        try:
            response = requests.post(url, data=params)
            response.raise_for_status()
            print("Telegram notification sent:", response.json())
        except requests.RequestException as e:
            print("Error sending Telegram notification:", e)