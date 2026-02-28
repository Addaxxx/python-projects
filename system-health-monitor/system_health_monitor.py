import psutil
import time
import os
import logging
import sys

def cpu_usage():
    return psutil.cpu_percent(interval=1)

def ram_usage():
    return psutil.virtual_memory().percent

def disk_usage():
    return psutil.disk_usage('/').percent

def check_threshold(value, threshold):
    if value > threshold:
        return "ALERT"
    return "OK"

def check_cpu(cpu_threshold):
    usage = cpu_usage()
    status = check_threshold(usage, cpu_threshold)
    logging.info(f"CPU Usage: {usage}% - Status: {status}")
    if status == "ALERT":
        logging.warning("CPU usage has exceeded the threshold!")
    print(f"CPU Usage: {usage}% - Status: {status}")
    
def check_ram(ram_threshold):
    usage = ram_usage()
    status = check_threshold(usage, ram_threshold)
    logging.info(f"RAM Usage: {usage}% - Status: {status}")
    if status == "ALERT":
        logging.warning("RAM usage has exceeded the threshold!")
    print(f"RAM Usage: {usage}% - Status: {status}")

def check_disk(disk_threshold):
    usage = disk_usage()
    status = check_threshold(usage, disk_threshold)
    logging.info(f"Disk Usage: {usage}% - Status: {status}")
    if status == "ALERT":
        logging.warning("Disk usage has exceeded the threshold!")
    print(f"Disk Usage: {usage}% - Status: {status}")

def main(): 
    logging.basicConfig(
    filename=sys.argv[5] if len(sys.argv) > 5 else 'system_health_monitor.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
    )

    logging.info("Starting System Health Monitor")

    cpu_threshold = float(sys.argv[1]) if len(sys.argv) > 1 else 80.0
    ram_threshold = float(sys.argv[2]) if len(sys.argv) > 2 else 80.0
    disk_threshold = float(sys.argv[3]) if len(sys.argv) > 3 else 90.0
    interval = float(sys.argv[4]) if len(sys.argv) > 4 else 60.0

    while True:
        check_cpu(cpu_threshold)
        check_ram(ram_threshold)
        check_disk(disk_threshold)
        time.sleep(interval) 

if __name__=="__main__":
    main()