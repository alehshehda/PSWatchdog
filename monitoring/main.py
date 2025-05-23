import threading
import time
import logging
import logging.handlers
import signal
import sys
import getpass

from process_monitor import monitor_system
from sftp_uploader import upload_files, init_sftp
from rules_loader import load_rules
from server_config import get_server_ip_and_port

# Global event for graceful shutdown
stop_event = threading.Event()

def setup_logging():
    """Setup logging with a timed rotating file handler."""
    file_handler = logging.handlers.TimedRotatingFileHandler(
        "error_log_main.txt", when="midnight", backupCount=7, encoding="utf-8"
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s [%(levelname)s] [%(threadName)s] %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S'
    ))
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(logging.Formatter(
        '%(asctime)s [%(levelname)s] [%(threadName)s] %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S'
    ))
    logging.basicConfig(level=logging.INFO, handlers=[file_handler, stream_handler])
    logging.info("Logging is set up with TimedRotatingFileHandler.")

def continuous_monitoring(rules, stop_event):
    """
    Continuously monitor processes.
    The monitor_system() function must accept stop_event as a parameter
    and check its state in its loop to exit gracefully.
    """
    try:
        monitor_system(rules, stop_event)
    except Exception as e:
        logging.error("Error in continuous_monitoring: %s", e, exc_info=True)

def continuous_upload(server_ip, stop_event, upload_interval=30, server_port=22):
    """
    Periodically run the upload_files() function.
    After each upload iteration, wait for upload_interval seconds (or break early if stop_event is set).
    """
    while not stop_event.is_set():
        try:
            upload_files(server_ip, server_port)
        except Exception as e:
            logging.error("Error in continuous_upload: %s", e, exc_info=True)
        # Wait upload_interval seconds in small increments to check stop_event regularly.
        for _ in range(upload_interval):
            if stop_event.is_set():
                break
            time.sleep(1)

def graceful_exit(signum, frame):
    """Handle graceful shutdown when receiving termination signals."""
    logging.info("Termination signal received. Shutting down...")
    stop_event.set()

def main():
    setup_logging()

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, graceful_exit)
    signal.signal(signal.SIGTERM, graceful_exit)

    logging.info("Loading rules...")
    rules = load_rules()
    if not rules:
        logging.warning("No rules loaded. Exiting.")
        sys.exit(0)

    server_ip, server_port = get_server_ip_and_port()
    logging.info("Initializing SFTP (UUID generation and remote directory creation)...")
    user = getpass.getuser()
    # One-time SFTP init: generate or load UUID and create remote user dir
    init_sftp(user, server_ip)

    logging.info("Starting continuous monitoring and periodic upload tasks...")
    # Create threads for monitoring and uploading
    monitor_thread = threading.Thread(target=continuous_monitoring, args=(rules, stop_event), name="MonitorThread")
    uploader_thread = threading.Thread(target=continuous_upload, args=(server_ip, stop_event, 30, server_port), name="UploaderThread")

    monitor_thread.start()
    uploader_thread.start()

    # Wait for both threads to finish
    monitor_thread.join()
    uploader_thread.join()

    logging.info("Program terminated gracefully.")

if __name__ == "__main__":
    main()
