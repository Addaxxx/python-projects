import docker
import logging
import os
import argparse
import time
import sys


def get_containers(client, container_name=None):
    """
    Get list of containers

    Args:
        client (docker.DockerClient): docker.DockerClient
        container_name (str): Name of the container. Defaults to None.

    Returns:
        list: List of containers
    """
    try:
        if container_name:
            containers = client.containers.list(
                all=True, filters={"name": container_name})
        else:
            containers = client.containers.list(all=True)
        return containers
    except docker.errors.DockerException as e:
        logging.error(f"Error fetching containers: {e}")
        return []


def get_container_stats(container):
    """
    Get the stats of the container

    Args:
        container (docker.models.containers.Container): A single container

    Returns:
        tuple: A tuple contianing the calcualte percentage for cpu and memory
    """
    try:
        stats = container.stats(stream=False)
        cpu_stats = stats['cpu_stats']
        precpu_stats = stats['precpu_stats']
        memory_stats = stats['memory_stats']

        cpu_delta = cpu_stats['cpu_usage']['total_usage'] \
            - precpu_stats['cpu_usage']['total_usage']

        system_delta = cpu_stats['system_cpu_usage'] \
            - precpu_stats['system_cpu_usage']

        num_cpus = cpu_stats['online_cpus']
        cpu_percent = (cpu_delta / system_delta) * num_cpus * 100

        memory_usage = memory_stats['usage']
        memory_limit = memory_stats['limit']
        memory_percent = (memory_usage / memory_limit) * 100

        calculated_stats = (cpu_percent, memory_percent)
        return calculated_stats
    except Exception as e:
        logging.error(f"Error retrieving stats: {e}")
        print(f"Error retrieving stats: {e}")
        return None


def monitor_containers(client, container_name,
                       cpu_threshold, memory_threshold):
    """
    Monitor the containers

    Args:
        client (docker.DockerClient): docker.DockerClient
        container_name (str): Name of the container
        cpu_threshold (float): User defined threshold for cpu
        memory_threshold (float): User defined threshold for memory
    """
    container_list = get_containers(client, container_name)
    for container in container_list:
        result = get_container_stats(container)
        if result is None:
            continue
        cpu_percent, memory_percent = result
        logging.info(f"ID = {container.id}, Name = {container.name}, "
                     f"Status = {container.status}, "
                     f"CPU% = {cpu_percent}, MEM% = {memory_percent}")
        print(f"ID = {container.id}, Name = {container.name}, "
              f"Status = {container.status}, "
              f"CPU% = {cpu_percent}, MEM% = {memory_percent}")
        if cpu_percent > cpu_threshold:
            logging.warning("CPU usage has exceeded the threshold!")
            print("CPU usage has exceeded the threshold!")
        if memory_percent > memory_threshold:
            logging.warning("Memory usage has exceeded the threshold!")
            print("Memory usage has exceeded the threshold!")


def main():
    parser = argparse.ArgumentParser(
        prog='Docker Container Monitor',
        description=(
            'A script to monitor Docker containers and log their status.'
        ),
        epilog=(
            'Example usage: python docker_monitor.py '
            '--log_file logs/docker_monitor.log'
        )
    )

    parser.add_argument(
        '-lf', '--log_file',
        type=str,
        help='Log file path (default: logs/docker_monitor.log)',
        default='logs/docker_monitor.log'
    )

    parser.add_argument(
        '-i', '--interval',
        type=int,
        help='Interval in seconds between status checks (default: 60)',
        default=60
    )

    parser.add_argument(
        '-cpu', '--cpu_threshold',
        type=float,
        help='CPU usage threshold percentage for alerts (default: 80.0)',
        default=80.0
    )

    parser.add_argument(
        '-mem', '--memory_threshold',
        type=float,
        help='Memory usage threshold percentage for alerts (default: 80.0)',
        default=80.0
    )

    parser.add_argument(
        '-c', '--container',
        type=str,
        help='Name or ID of the container to '
        'monitor (default: all containers)',
        default=None
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

    logging.info('Starting Docker Container Monitor')

    try:
        client = docker.from_env()
    except docker.errors.DockerException as e:
        logging.error(f"Failed to connect to Docker: {e}")
        sys.exit(1)

    while True:
        monitor_containers(client, args.container,
                           args.cpu_threshold, args.memory_threshold)
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
