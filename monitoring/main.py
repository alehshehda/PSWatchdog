import threading
import traceback
import datetime
import time
from process_monitor import monitor_system
from sftp_uploader import upload_files_periodically
from rules_loader import load_rules


def log_error(log_filename, error_message):
    """Writes an error message to a specified log file with a timestamp."""
    timestamp = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
    with open(log_filename, "a") as f:
        f.write(f"{timestamp}\n{error_message}\n{'-' * 50}\n")


def safe_monitor(rules):
    """Runs the process monitoring function with error handling to prevent crashes."""
    while True:
        try:
            monitor_system(rules)  # Pass preloaded rules to avoid reloading them in each iteration
        except Exception as e:
            error_message = f"Error in monitor_system: {str(e)}\n{traceback.format_exc()}"
            log_error("error_log_monitor.txt", error_message)
            print(f"Error in monitoring: {str(e)}. Continuing execution...")


def safe_upload():
    """Runs the file upload function with error handling to prevent crashes."""
    while True:
        try:
            upload_files_periodically()
        except Exception as e:
            error_message = f"Error in upload_files_periodically: {str(e)}\n{traceback.format_exc()}"
            log_error("error_log_upload.txt", error_message)
            print(f"Error in file upload: {str(e)}. Continuing execution...")


def main():
    try:
        print("Loading rules...")
        rules = load_rules()  # Load rules before starting threads
        
        if not rules:
            print("No rules loaded. Exiting.")
            return  # Stop execution if rules failed to load

        print("Starting process monitoring and file upload...")

        # Start process monitoring in a separate thread
        monitor_thread = threading.Thread(target=safe_monitor, args=(rules,))
        monitor_thread.daemon = True  # Ensure the thread terminates when the main program exits
        monitor_thread.start()

        # Start file upload in a separate thread
        upload_thread = threading.Thread(target=safe_upload)
        upload_thread.daemon = True
        upload_thread.start()

        # Keep the program running indefinitely
        while True:
            time.sleep(1)  # Prevents high CPU usage by adding a small delay

    except Exception as e:
        error_message = f"Critical error in main: {str(e)}\n{traceback.format_exc()}"
        log_error("error_log_main.txt", error_message)
        print(f"Critical error: {str(e)}. Details saved in error_log_main.txt")


if __name__ == "__main__":
    main()
