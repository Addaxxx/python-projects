import logging
import os
import argparse
import shutil
import tarfile
import zipfile
import datetime as dt
import fnmatch
import sys


def create_tar_gz(source, destination, exclude):
    """
    Creates a tar archive of the specified source directory,
    excluding specified files

    Args:
        source (str): Source directory to backup
        destination (str): Destination file path for the tar.gz archive
        exclude (list):  Pattern to exclude files (e.g., *.log)
    """
    try:
        with tarfile.open(destination, 'w:gz') as tar:
            for root, dirs, files in os.walk(source):
                for file in files:
                    file_path = os.path.join(root, file)
                    if exclude and any(fnmatch.fnmatch(file, pattern)
                                       for pattern in exclude):
                        logging.warning(f"Excluding file: {file_path}")
                        continue
                    # arcname strips the absolute path so
                    # archive contains relative paths only.
                    tar.add(file_path,
                            arcname=os.path.relpath(file_path, source))
                    logging.info(f"Added file to archive: {file_path}")
        logging.info(f"Created tar.gz archive at: {destination}")
        print(f"Created tar.gz archive at: {destination}")
    except Exception as e:
        logging.error(f"Error creating tar.gz archive: {e}")
        print(f"Error creating tar.gz archive: {e}")
        sys.exit(1)


def create_zip(source, destination, exclude):
    """
    Creates a zip archive of the specified source directory,
    excluding specified files

    Args:
        source (str): Source directory to backup
        destination (str): Destination file path for the zip archive
        exclude (list): Pattern to exclude files (e.g., *.log)
    """
    try:
        with zipfile.ZipFile(destination, 'w') as zipf:
            for root, dirs, files in os.walk(source):
                for file in files:
                    file_path = os.path.join(root, file)
                    if exclude and any(fnmatch.fnmatch(file, pattern)
                                       for pattern in exclude):
                        logging.warning(f"Excluding file: {file_path}")
                        continue
                    # arcname strips the absolute path so archive
                    # contains relative paths only.
                    zipf.write(file_path,
                               arcname=os.path.relpath(file_path, source))
                    logging.info(f"Added file to archive: {file_path}")
        logging.info(f"Created zip archive at: {destination}")
        print(f"Created zip archive at: {destination}")
    except Exception as e:
        logging.error(f"Error creating zip archive: {e}")
        print(f"Error creating zip archive: {e}")
        sys.exit(1)


def backup_directory(source, destination, compression, exclude):
    """
    Backups a directory by creating a compressed archive or copying it directly

    Args:
        source (str): Source directory to backup
        destination (str): Destination directory to save the backup
        compression (str): Compression format (tar.gz, zip, or none)
        exclude (list): Pattern to exclude files (e.g., *.log)

    Returns:
        str: Path to the backup directory or archive created
    """
    try:
        date = dt.datetime.now(dt.timezone.utc)
        # Use UTC timestamp to ensure unique,
        # timezone-consistent backup folder names.
        formatted_date = date.strftime('%Y-%m-%dT%H-%M-%S')
        backup_dir = os.path.join(destination, formatted_date)
        os.makedirs(backup_dir)
        logging.info(f"Created backup directory: {backup_dir}")
        if compression == 'tar.gz':
            archive_path = os.path.join(backup_dir,
                                        f"{os.path.basename(source)}.tar.gz")
            create_tar_gz(source, archive_path, exclude)
        elif compression == 'zip':
            archive_path = os.path.join(backup_dir,
                                        f"{os.path.basename(source)}.zip")
            create_zip(source, archive_path, exclude)
        else:
            shutil.copytree(source,
                            os.path.join(backup_dir, os.path.basename(source)))
            logging.info(f"Copied directory without "
                         f"compression to: {backup_dir}")
        print(f"Backup created at: {backup_dir}")
        return backup_dir
    except Exception as e:
        logging.error(f"Error during backup: {e}")
        print(f"Error during backup: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        prog='Directory Backup',
        description=(
            'A script to backup a directory with support for compression.'
        ),
        epilog=(
            'Example usage: python directory_backup.py '
            '--source /path/to/source '
            '--destination /path/to/destination --exclude *.log'
        )
    )

    parser.add_argument(
        '-s', '--source',
        type=str,
        help='Source directory to backup',
        required=True,
    )

    parser.add_argument(
        '-d', '--destination',
        type=str,
        help='Destination directory to save the backup',
        required=True,
    )

    parser.add_argument(
        '-e', '--exclude',
        type=str,
        help='Pattern to exclude files (e.g., *.log)',
        default=None,
        nargs='*'
    )

    parser.add_argument(
        '-lf', '--log_file',
        type=str,
        help='Log file path (default: logs/directory_backup.log)',
        default='logs/directory_backup.log'
    )

    parser.add_argument(
        '-c', '--compression',
        type=str,
        help='Compression format (tar.gz, zip, etc.)',
        default='tar.gz',
        choices=['tar.gz', 'zip', 'none']
    )

    args = parser.parse_args()

    # Build log path relative to the script, not the working directory.
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)

    logging.basicConfig(filename=os.path.join
                        (log_dir, os.path.basename(args.log_file)),
                        level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    logging.info(f"Starting backup of {args.source} to "
                 f"{args.destination} with compression {args.compression}")
    print(f"Starting backup of {args.source} to "
          f"{args.destination} with compression {args.compression}")

    source = os.path.abspath(args.source)
    destination = os.path.abspath(args.destination)

    if not os.path.exists(source):
        logging.error(f"Source directory {source} does not exist.")
        print(f"Source directory {source} does not exist.")
        sys.exit(1)

    # Destination must not be inside source — would cause recursive backup.
    if os.path.abspath(destination).startswith(os.path.abspath(source)):
        logging.error(f"Destination directory {destination} "
                      f"is inside the source directory {source}. "
                      f"This can cause issues with the backup process.")
        sys.exit(1)

    backup_directory(source, destination, args.compression, args.exclude)


if __name__ == '__main__':
    main()
