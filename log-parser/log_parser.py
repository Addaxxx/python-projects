import argparse
import re
import os
import sys
import logging


def read_file(log_file):
    try:
        with open(log_file, "r") as f:
            return f.readlines()
    except FileNotFoundError:
        logging.error(f"File not found: {log_file}")
        print(f"Error: File not found - {log_file}")
    except Exception as e:
        logging.error(f"Unexpected error reading file: {e}")
        print(f"Unexpected error reading file: {e}")


def identify_log_level(line):
    log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    for word in line.split():
        if word in log_levels:
            return word
    return "UNKNOWN"


def count_log_levels(lines):
    log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', "UNKNOWN"]
    log_counts = {level: 0 for level in log_levels}
    for line in lines:
        level = identify_log_level(line)
        if level in log_levels:
            log_counts[level] += 1
    return log_counts


def print_summary(log_counts):
    total_lines = sum(log_counts.values())
    print(f"Total lines: {total_lines}")
    for x in log_counts:
        if log_counts[x] > 0:
            print(f"{x}: {log_counts[x]}")


def main():
    parser = argparse.ArgumentParser(
        prog='Log Parser',
        description=(
            'A simple log parser that reads and displays'
            'the contents of a log file.'
        ),
        epilog=(
            'Example usage: python3 log_parser.py'
        )
    )

    parser.add_argument(
           '-lf', '--log_file',
           type=str,
           help='Path to the log file to be parsed (default: log.txt)',
    )

    args = parser.parse_args()

    lines = read_file(args.log_file)
    counts = count_log_levels(lines)
    print_summary(counts)


if __name__ == "__main__":
    main()
