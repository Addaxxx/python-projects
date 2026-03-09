import psutil
import time
import os
import logging
import argparse
import sys
import yaml
import smtplib
import ssl
from dotenv import load_dotenv


def cpu_usage():
    """
    Get current CPU usage percentage.

    Returns:
        float: CPU usage percentage
    """
    return psutil.cpu_percent(interval=1)


def ram_usage():
    """
    Get current RAM usage percentage.

    Returns:
        float: RAM usage percentage
    """
    return psutil.virtual_memory().percent


def disk_usage(disk_path):
    """
    Get current disk usage percentage for a given path.

    Args:
        disk_path (str): Path to check disk usage

    Returns:
        float: Disk usage percentage
    """
    return psutil.disk_usage(disk_path).percent


def check_all_partitions():
    """
    Get all disk partitions.

    Returns:
        list: List of disk partitions
    """
    return psutil.disk_partitions()


def check_threshold(value, threshold):
    """
    Check if a value exceeds the threshold.

    Args:
        value (float): Current value
        threshold (float): Threshold value

    Returns:
        str: "ALERT" if value > threshold, "OK" otherwise
    """
    if value > threshold:
        return "ALERT"
    return "OK"


def check_cpu(cpu_threshold):
    """
    Check CPU usage and log results.

    Args:
        cpu_threshold (float): CPU usage threshold percentage
    """
    try:
        usage = cpu_usage()
        status = check_threshold(usage, cpu_threshold)
        logging.info(f"CPU Usage: {usage}% - Status: {status}")
        if status == "ALERT":
            logging.warning("CPU usage has exceeded the threshold!")
            send_notification(subject="CPU Usage Alert",
                              body=f"CPU usage has exceeded the threshold! "
                              f"Current usage: {usage}%")
        print(f"CPU Usage: {usage}% - Status: {status}")
    except psutil.Error:
        logging.error("Failed to retrieve CPU usage.")
        print("Error: Failed to retrieve CPU usage.")
    except Exception as e:
        logging.error(f"Unexpected error checking CPU: {e}")
        print(f"Unexpected error checking CPU: {e}")


def check_ram(ram_threshold):
    """
    Check RAM usage and log results.

    Args:
        ram_threshold (float): RAM usage threshold percentage
    """
    try:
        usage = ram_usage()
        status = check_threshold(usage, ram_threshold)
        logging.info(f"RAM Usage: {usage}% - Status: {status}")
        if status == "ALERT":
            logging.warning("RAM usage has exceeded the threshold!")
            send_notification(subject="RAM Usage Alert",
                              body=f"RAM usage has exceeded the threshold! "
                              f"Current usage: {usage}%")
        print(f"RAM Usage: {usage}% - Status: {status}")
    except psutil.Error:
        logging.error("Failed to retrieve RAM usage.")
        print("Error: Failed to retrieve RAM usage.")
    except Exception as e:
        logging.error(f"Unexpected error checking RAM: {e}")
        print(f"Unexpected error checking RAM: {e}")


def check_single_disk(disk_threshold, disk_path):
    """
    Check disk usage for a single path and log results.

    Args:
        disk_threshold (float): Disk usage threshold percentage
        disk_path (str): Path to check disk usage
    """
    try:
        usage = disk_usage(disk_path)
        status = check_threshold(usage, disk_threshold)
        logging.info(f"Disk Usage for "
                     f"{disk_path}: {usage}% - Status: {status}")
        print(f"Disk Usage for {disk_path}: {usage}% - Status: {status}")
        if status == "ALERT":
            logging.warning("Disk usage has exceeded the threshold!")
            send_notification(subject="Disk Usage Alert",
                              body=f"Disk usage for {disk_path} "
                              "has exceeded the threshold! "
                              f"Current usage: {usage}%")
    except psutil.Error:
        logging.error(f"Failed to retrieve disk usage for {disk_path}.")
        print(f"Error: Failed to retrieve disk usage for {disk_path}.")
    except Exception as e:
        logging.error(
            f"Unexpected error checking disk usage for {disk_path}: {e}")
        print(f"Unexpected error checking disk usage for {disk_path}: {e}")


def check_disk(disk_threshold, disk_path, all_partitions):
    """
    Check disk usage for specified path or all partitions.

    Args:
        disk_threshold (float): Disk usage threshold percentage
        disk_path (str): Path to check disk usage
        all_partitions (list): List of all partitions to check
    """
    if all_partitions:
        for path in all_partitions:
            check_single_disk(disk_threshold, path.mountpoint)
    elif os.path.exists(disk_path):
        check_single_disk(disk_threshold, disk_path)
    else:
        logging.error(f"Disk path {disk_path} does not exist.")
        print(f"Error: Disk path {disk_path} does not exist.")


def load_config(config_file):
    """
    Load configuration from YAML file.

    Args:
        config_file (str): Path to YAML configuration file

    Returns:
        dict: Configuration dictionary
    """
    try:
        with open(config_file, 'r') as file:
            return yaml.safe_load(file) or {}
    except Exception as e:
        logging.error(f"Failed to load configuration file {config_file}: {e}")
        print(f"Error: Failed to load configuration file {config_file}: {e}")
        sys.exit(1)


def send_notification(subject, body):
    """
    Send an email notification via Gmail SMTP.

    Args:
        subject (str): Notification subject
        body (str): Notification body
    """
    try:
        email_address = os.getenv("EMAIL_ADDRESS")
        email_password = os.getenv("EMAIL_PASSWORD")
        email_recipient = os.getenv("EMAIL_RECIPIENT")
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465,
                              context=context) as server:
            server.login(email_address,
                         email_password)
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(email_address,
                            email_recipient, message)
        logging.info(f"Notification sent - Subject: {subject}, Body: {body}")
        print(f"Notification sent - Subject: {subject}, Body: {body}")
    except Exception as e:
        logging.error(f"Failed to send notification: {e}")
        print("Error: Failed to send notification.")


def main():
    # Load environment variables from .env file before anything else.
    load_dotenv()

    parser = argparse.ArgumentParser(
        prog='System Health Monitor',
        description=(
            'Monitors CPU, RAM, and Disk usage and logs alerts'
            'when thresholds are exceeded.'
        ),
        epilog=(
            'Example usage: python3 system_health_monitor.py'
            '--cpu_threshold 75 --interval 30'
        )
    )

    parser.add_argument(
        '-ct', '--cpu_threshold',
        type=float,
        default=80.0,
        help='CPU usage threshold percentage (default: 80.0)'
    )

    parser.add_argument(
        '-rt', '--ram_threshold',
        type=float,
        default=80.0,
        help='RAM usage threshold percentage (default: 80.0)'
    )

    parser.add_argument(
        '-dt', '--disk_threshold',
        type=float,
        default=90.0,
        help='Disk usage threshold percentage (default: 90.0)'
    )

    parser.add_argument(
        '-i', '--interval',
        type=float,
        default=60.0,
        help='Monitoring interval in seconds (default: 60.0)'
    )

    parser.add_argument(
        '-dp', '--disk_path',
        type=str,
        default='/',
        help='Path to monitor disk usage (default: "/")'
    )

    parser.add_argument(
        '-lf', '--log_file',
        type=str,
        default='logs/system_health_monitor.log',
        help='Log file path (default: system_health_monitor.log)'
    )

    parser.add_argument(
        '-c', '--config',
        type=str,
        help='Path to YAML configuration file'
    )

    parser.add_argument(
        '-ap', '--all_partitions',
        action='store_true',
        help='Check disk usage for all partitions (overrides --disk_path)'
    )

    args = parser.parse_args()

    # Build log path relative to the script, not the working directory.
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)

    logging.basicConfig(
        filename=os.path.join(log_dir, os.path.basename(args.log_file)),
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    logging.info(f"Starting System Health Monitor with CPU threshold:"
                 f"{args.cpu_threshold}%, "
                 f"RAM threshold: {args.ram_threshold}%, "
                 f"Disk threshold: {args.disk_threshold}%")
    logging.info(f"Monitoring interval: {args.interval} seconds")
    logging.info(f"Log file: "
                 f"{os.path.join(log_dir, os.path.basename(args.log_file))}")

    # Fail fast if email credentials are missing
    # as notifications won't work without them.
    if (not os.getenv("EMAIL_ADDRESS")
            or not os.getenv("EMAIL_PASSWORD")
            or not os.getenv("EMAIL_RECIPIENT")):
        logging.error("Email credentials are "
                      "not fully set in environment variables.")
        print("Warning: Email credentials are "
              "not fully set in environment variables. "
              "Notifications will not be sent.")
        sys.exit(1)

    if not 0 <= args.cpu_threshold <= 100:
        print("Error: CPU threshold must be between 0 and 100")
        sys.exit(1)
    if not 0 <= args.ram_threshold <= 100:
        print("Error: RAM threshold must be between 0 and 100")
        sys.exit(1)
    if not 0 <= args.disk_threshold <= 100:
        print("Error: Disk threshold must be between 0 and 100")
        sys.exit(1)

    # Config loading priority:
    # explicit --config flag > config.yaml > config.yml
    config = {}
    if args.config:
        config = load_config(args.config)
    elif os.path.exists('config.yaml'):
        config = load_config('config.yaml')
    elif os.path.exists('config.yml'):
        config = load_config('config.yml')

    if 'thresholds' in config:
        if 'cpu' in config['thresholds']:
            args.cpu_threshold = float(config['thresholds']['cpu'])
        if 'ram' in config['thresholds']:
            args.ram_threshold = float(config['thresholds']['ram'])
        if 'disk' in config['thresholds']:
            args.disk_threshold = float(config['thresholds']['disk'])

    if args.all_partitions:
        logging.info("Monitoring all disk partitions")
        print("Monitoring all disk partitions")

    # Only collect partition list once at startup, not on every loop iteration.
    all_partitions = check_all_partitions() if args.all_partitions else None

    try:
        while True:
            check_cpu(args.cpu_threshold)
            check_ram(args.ram_threshold)
            check_disk(args.disk_threshold, args.disk_path,
                       all_partitions)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        logging.info("System Health Monitor stopped by user")
        print("System Health Monitor stopped by user")
    except Exception as e:
        logging.error(f"Unexpected error in monitoring loop: {e}")
        print(f"Unexpected error in monitoring loop: {e}")
    finally:
        logging.info("System Health Monitor shutting down")
        print("System Health Monitor shutting down")


if __name__ == "__main__":
    main()
