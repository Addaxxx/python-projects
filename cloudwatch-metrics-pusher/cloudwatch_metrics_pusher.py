import logging
import sys
import argparse
import datetime as dt
import os
import time
import psutil
import boto3
import botocore.exceptions


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


def get_system_metrics(disk_path):
    """
    Put system metrics into a dictionary

    Args:
        disk_path (str): Path to check disk usage

    Returns:
        dict: A dictionary containing the
        key:value pairs for system metrics
    """
    system_metrics = {
        'cpu': cpu_usage(),
        'memory': ram_usage(),
        'disk': disk_usage(disk_path)
    }

    return system_metrics


def push_metrics(cloudwatch_client, namespace, metrics):
    """
    Push system metrics to AWS Cloudwatch

    Args:
        cloudwatch_client (boto3.client): Cloudwatch client instance used
        to connect to AWS cloudwatch.

        namespace (str): AWS Namespace

        metrics (dict): A dictionary containing
        key:value pairs for system metrics
    """
    try:
        timestamp = dt.datetime.now(dt.timezone.utc)
        for metric_name, value in metrics.items():
            cloudwatch_client.put_metric_data(
                Namespace=namespace,
                MetricData=[
                    {
                        'MetricName': metric_name,
                        'Timestamp': timestamp,
                        'Value': value,
                        'Unit': 'Percent'
                    }
                ]
            )
            logging.info(f"Pushed metric {metric_name}: {value}")
            print(f"Pushed metric {metric_name}: {value}")
    except botocore.exceptions.ClientError as e:
        logging.error(f"Failed to push metrics: {e}")
        print(f"Failed to push metrics: {e}")
    except Exception as e:
        logging.error(f"Error pushing metrics: {e}")
        print(f"Error pushing metrics: {e}")


def main():
    parser = argparse.ArgumentParser(
        prog='Cloudwatch Metrics Pusher',
        description=(
            'A script to monitor system metrics and push to AWS Cloudwatch.'
        ),
        epilog=(
            'Example usage: python3 cloudwatch_metrics_pusher.py '
        )
    )

    parser.add_argument(
        '-lf', '--log_file',
        type=str,
        help='Log file path (default: logs/cloudwatch_metrics_pusher.log)',
        default='logs/cloudwatch_metrics_pusher.log'
    )

    parser.add_argument(
        '-i', '--interval',
        type=int,
        help='Interval in seconds between status checks (default: 60)',
        default=60
    )

    parser.add_argument(
        '-ns', '--namespace',
        type=str,
        help='CloudWatch namespace string e.g. Custom/SystemMetrics',
        required=True
    )

    parser.add_argument(
        '-r', '--region',
        type=str,
        help='AWS region',
        required=True
    )

    parser.add_argument(
        '-dp', '--disk_path',
        type=str,
        help='Disk path to monitor (default: /)',
        default='/'
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

    logging.info('Starting Cloudwatch Metrics Pusher')
    logging.info(f"Arguments: log_file={args.log_file}, "
                 f"interval={args.interval}, "
                 f"namespace={args.namespace}, "
                 f"region={args.region}, "
                 f"disk_path={args.disk_path}")
    print('Starting Cloudwatch Metrics Pusher')

    region_name = args.region

    try:
        cloudwatch_client = boto3.client('cloudwatch', region_name=region_name)
    except botocore.exceptions.ClientError as e:
        logging.error(f"Failed to connect to Cloudwatch: {e}")
        sys.exit(1)

    try:
        while True:
            metrics = get_system_metrics(args.disk_path)
            push_metrics(cloudwatch_client, args.namespace, metrics)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        logging.info("CloudWatch Metrics Pusher stopped by user.")
        print("CloudWatch Metrics Pusher Monitor stopped.")
        sys.exit(0)


if __name__ == "__main__":
    main()
