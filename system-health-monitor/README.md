# System Health Monitor

A Python based system health monitoring tool that tracks CPU, RAM and disk usage and alerts when usage exceeds defined thresholds. Built as part of my journey in learning Python.

## Features

- Monitors CPU, RAM and disk usage in real time
- Displays OK or ALERT status based on configurable thresholds
- Runs continuously on a configurable interval
- Writes all results to a log file with timestamps
- WARNING level log entries for ALERT events
- Graceful error handling — program continues running if one check fails
- Fully configurable via command line arguments

## Requirements

- Python 3.x
- psutil

## Installation

**1. Clone the repo**
```bash
git clone https://github.com/Addaxxx/python-projects.git
cd python-projects/system-health-monitor
```

**2. Create and activate a virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install psutil
```

## Usage

Run with default settings:
```bash
python3 system_health_monitor.py
```

Run with custom settings:
```bash
python3 system_health_monitor.py --cpu_threshold 75 --ram_threshold 75 --disk_threshold 85 --interval 30 --disk_path / --log_file system_health_monitor.log
```

## Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--cpu_threshold` | 80.0 | CPU usage alert threshold (%) |
| `-rt, --ram_threshold` | 80.0 | RAM usage alert threshold (%) |
| `-dt, --disk_threshold` | 90.0 | Disk usage alert threshold (%) |
| `-i, --interval` | 60.0 | Monitoring interval in seconds |
| `-dp, --disk_path` | `/` | Disk path to monitor |
| `-lf, --log_file` | `logs/system_health_monitor.log` | Log file path |

## Example Output

```
CPU Usage: 23.5% - Status: OK
RAM Usage: 61.2% - Status: OK
Disk Usage: 78.4% - Status: OK
```

## Log File

All results are written to the `logs/` folder relative to the script location. INFO entries are written for all checks and WARNING entries are written when a threshold is exceeded.

Example log entries:
```
2026-03-01 12:00:00,000 - INFO - CPU Usage: 23.5% - Status: OK
2026-03-01 12:00:00,001 - WARNING - CPU usage has exceeded the threshold!
```

