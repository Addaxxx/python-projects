import argparse
import sys
import os
import logging


def read_file(log_file):
    """
    Read the contents of the specified log file and return a list of lines.

    Args:
        log_file (str): Path to the log file to be read.

    Returns:
        list: A list of lines, one per line read from the log file.
    """
    try:
        with open(log_file, "r") as f:
            return f.readlines()
    except FileNotFoundError:
        logging.error(f"File not found: {log_file}")
        print(f"Error: File not found - {log_file}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error reading file: {e}")
        print(f"Unexpected error reading file: {e}")
        sys.exit(1)


def identify_log_level(line):
    """
    Identify the log level in a given line of text. The function checks for
    ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

    Args:
        line (str): A single line of text from the log file.

    Returns:
        str: The identified log level if found, otherwise "UNKNOWN".
    """
    log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    for word in line.split():
        if word in log_levels:
            return word
    return "UNKNOWN"


def count_log_levels(lines):
    """
    Count the occurrences of each log level in the provided lines.

    Args:
        lines (list): A list of lines from the log file.

    Returns:
        dict: A dictionary with log levels as
        keys and their respective counts as values.
    """
    log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    log_counts = {level: 0 for level in log_levels}
    for line in lines:
        level = identify_log_level(line)
        if level in log_levels:
            log_counts[level] += 1
    return log_counts


def filter_lines(lines, filter_level):
    """
    Filter the provided lines based on the specified log level.

    Args:
        lines (list): A list of lines from the log file.

        filter_level (str): The log level to filter by
        (e.g., 'ERROR', 'WARNING').

    Returns:
        list: A list of lines that contain the specified log level.
        If the filter level is invalid, returns None.
    """
    log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    filtered_lines = []
    if filter_level not in log_levels:
        print(f"Invalid filter level: {filter_level}. "
              f"Valid levels are: {', '.join(log_levels[:-1])}")
        logging.error(f"Invalid filter level: {filter_level}. "
                      f"Valid levels are: {', '.join(log_levels[:-1])}")
        return
    else:
        for line in lines:
            words = line.split()
            if filter_level in words:
                filtered_lines.append(line)
    return filtered_lines


def print_summary(log_counts, filter_level, filtered_lines):
    """
    Print a summary of the log counts and optionally
    filtered lines based on the specified log level.

    Args:
        log_counts (dict): A dictionary with log levels
        as keys and their respective counts as values.

        filter_level (str): The log level used for filtering
        (e.g., 'ERROR', 'WARNING'). If None,
        prints total counts for all levels.

        filtered_lines (list): A list of lines
        that contain the specified log level.
        If filter_level is None, this will be the original list of lines.
    """
    if filter_level:
        print(f"Lines containing"
              f" '{filter_level}': {log_counts.get(filter_level, 0)}")
        logging.info(f"Lines containing '{filter_level}': "
                     f"{log_counts.get(filter_level, 0)}")
        for line in filtered_lines:
            print(line.strip())
    else:
        total_lines = sum(log_counts.values())
        print(f"Total lines: {total_lines}")
        logging.info(f"Total lines: {total_lines}")
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
           required=True
    )

    parser.add_argument(
           '-f', '--filter',
           type=str,
           help='Optional filter to display only lines containing'
           'a specific log level (e.g., ERROR, WARNING)',
    )

    args = parser.parse_args()

    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)

    logging.basicConfig(
        filename=os.path.join(log_dir, 'log_parser.log'),
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    logging.info(f"Parsing logs from"
                 f"{args.log_file} with filter: {args.filter}")

    lines = read_file(args.log_file)

    if not lines:
        print("No lines to process. File may be empty")
        logging.error("No lines to process. File may be empty.")
        sys.exit(1)

    counts = count_log_levels(lines)
    filtered_lines = filter_lines(lines, args.filter) if args.filter else lines

    if filtered_lines is None:
        sys.exit(1)
    else:
        print_summary(counts, args.filter, filtered_lines)


if __name__ == "__main__":
    main()
