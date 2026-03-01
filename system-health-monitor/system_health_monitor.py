import psutil
import time
import os
import logging
import argparse

def cpu_usage():
    return psutil.cpu_percent(interval=1)

def ram_usage():
    return psutil.virtual_memory().percent

def disk_usage(disk_path):
    return psutil.disk_usage(disk_path).percent

def check_threshold(value, threshold):
    if value > threshold:
        return "ALERT"
    return "OK"

def check_cpu(cpu_threshold):
    try:
        usage = cpu_usage()
        status = check_threshold(usage, cpu_threshold)
        logging.info(f"CPU Usage: {usage}% - Status: {status}")
        if status == "ALERT":
            logging.warning("CPU usage has exceeded the threshold!")
        print(f"CPU Usage: {usage}% - Status: {status}")
    except psutil.Error:
        logging.error("Failed to retrieve CPU usage.")
        print("Error: Failed to retrieve CPU usage.")
    except Exception as e:
        logging.error(f"Unexpected error checking CPU: {e}")
        print(f"Unexpected error checking CPU: {e}")
    
def check_ram(ram_threshold):
    try:
        usage = ram_usage()
        status = check_threshold(usage, ram_threshold)
        logging.info(f"RAM Usage: {usage}% - Status: {status}")
        if status == "ALERT":
            logging.warning("RAM usage has exceeded the threshold!")
        print(f"RAM Usage: {usage}% - Status: {status}")
    except psutil.Error:
        logging.error("Failed to retrieve RAM usage.")
        print("Error: Failed to retrieve RAM usage.")
    except Exception as e:
        logging.error(f"Unexpected error checking RAM: {e}")
        print(f"Unexpected error checking RAM: {e}")

def check_disk(disk_threshold, disk_path):
    if os.path.exists(disk_path):
        try:
            usage = disk_usage(disk_path) 
            status = check_threshold(usage, disk_threshold)
            logging.info(f"Disk Usage: {usage}% - Status: {status}")
            if status == "ALERT":
                logging.warning("Disk usage has exceeded the threshold!")
            print(f"Disk Usage: {usage}% - Status: {status}")
        except psutil.Error:
            logging.error(f"Failed to retrieve disk usage for {disk_path}.")
            print(f"Error: Failed to retrieve disk usage for {disk_path}.")
        except Exception as e:
            logging.error(f"Unexpected error checking disk usage for {disk_path}: {e}")
            print(f"Unexpected error checking disk usage for {disk_path}: {e}")
    else:
        logging.error(f"Disk path {disk_path} does not exist.")
        print(f"Error: Disk path {disk_path} does not exist.")

def main(): 
    parser = argparse.ArgumentParser(
        prog='System Health Monitor',
        description='Monitors CPU, RAM, and Disk usage and logs alerts when thresholds are exceeded.',
        epilog='Example usage: python3 system_health_monitor.py --cpu_threshold 75 --interval 30'
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

    args = parser.parse_args()
    
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        filename=os.path.join(log_dir, os.path.basename(args.log_file)),
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    logging.info("Starting System Health Monitor")
    logging.info(f"Checking disk usage for {args.disk_path}")   
      
    while True:
        check_cpu(args.cpu_threshold)
        check_ram(args.ram_threshold)
        check_disk(args.disk_threshold, args.disk_path)
        time.sleep(args.interval) 

if __name__=="__main__":
    main()