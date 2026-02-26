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
    status = check_threshold(usage, 80)
    print(f"CPU Usage: {usage}% - Status: {status}")
    
def check_ram():
    usage = ram_usage()
    status = check_threshold(usage, 80)
    print(f"RAM Usage: {usage}% - Status: {status}")

def check_disk():
    usage = disk_usage()
    status = check_threshold(usage, 90)
    print(f"Disk Usage: {usage}% - Status: {status}")

check_cpu()
check_ram()
check_disk()