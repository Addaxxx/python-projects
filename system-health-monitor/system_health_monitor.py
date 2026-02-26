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

def check_cpu():
    usage = cpu_usage()
    status = check_threshold(usage, cpu_threshold)
    print(f"CPU Usage: {usage}% - Status: {status}")
    
def check_ram():
    usage = ram_usage()
    status = check_threshold(usage, ram_threshold)
    
    print(f"RAM Usage: {usage}% - Status: {status}")

def check_disk():
    usage = disk_usage()
    status = check_threshold(usage, disk_threshold)
    print(f"Disk Usage: {usage}% - Status: {status}")


cpu_threshold = float(sys.argv[1]) if len(sys.argv) > 1 else 80.0
ram_threshold = float(sys.argv[2]) if len(sys.argv) > 2 else 80.0
disk_threshold = float(sys.argv[3]) if len(sys.argv) > 3 else 90.0
interval = float(sys.argv[4]) if len(sys.argv) > 4 else 60.0

while True:
    check_cpu()
    check_ram()
    check_disk()
    time.sleep(interval)
