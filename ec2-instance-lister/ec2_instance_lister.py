import logging
import os
import argparse
import csv
import boto3
import botocore.exceptions


def state_filter(state):
    """
    Create a filter for EC2 instance state.

    Args:
        state (str): The desired state of
        the EC2 instances (e.g., 'running', 'stopped').

    Returns:
        list: A list of filters for EC2 instance state.
    """
    filters = []

    if state:
        filters.append({
            "Name": "instance-state-name",
            "Values": [state]
        })

    return filters


def scan_regions(regions, filters, writer):
    """
    Scan specified AWS regions for EC2 instances matching the provided filters.

    Args:
        regions (list): A list of AWS regions to scan for EC2 instances.

        filters (list): A list of filters to
        apply when describing EC2 instances.

        writer (csv.writer): A CSV writer object to write
        instance details to a CSV file.
        
    Returns:
    int: The total number of EC2 instances found across all scanned regions.
    """
    total_instances = 0
    for region_name in regions:
        try:
            logging.info(f"Listing EC2 instances in region: "
                         f"{region_name}")
            print(f"Listing EC2 instances in region: {region_name}")
            regional_ec2_client = boto3.client('ec2', region_name=region_name)
            # Use a paginator instead of describe_instances() directly —
            # describe_instances caps at 1000 results per call
            # without pagination.
            paginator = regional_ec2_client.get_paginator("describe_instances")
            for page in paginator.paginate(Filters=filters):
                for reservation in page.get("Reservations", []):
                    total_instances += len(reservation.get("Instances", []))
                list_ec2_instances(page, region_name, writer)
        except botocore.exceptions.ClientError as e:
            # Some regions require explicit opt-in in the AWS console.
            # Skip them rather than failing the entire scan.
            if e.response['Error']['Code'] == 'AuthFailure':
                logging.warning(f"Skipping {region_name} — auth failure.")
                print(f"Skipping {region_name} — not authorized.")
                continue
            logging.error(f"ClientError in {region_name}: {e}")
            print(f"ClientError in {region_name}: {e}")
    return total_instances


def list_ec2_instances(response, region_name, writer):
    """
    Process the response from describe_instances and print instance details.

    Args:
        response (dict): The response from the describe_instances API call
        containing EC2 instance details.

        region_name (str): The name of the AWS region being processed.

        writer (csv.writer): A CSV writer object to write
        instance details to a CSV file.
        If None, instance details will not be written to a file.
    """
    try:
        for reservation in response.get('Reservations', []):
            for instance in reservation.get('Instances', []):
                instance_id = instance.get('InstanceId', 'N/A')
                instance_type = instance.get('InstanceType', 'N/A')
                state = instance.get("State", {}).get("Name", "N/A")
                ip_address = instance.get('PublicIpAddress', 'N/A')
                if writer is not None:
                    writer.writerow([region_name, instance_id,
                                    instance_type, state, ip_address])
                logging.info(f"Instance ID: {instance_id}, "
                             f"Type: {instance_type}, "
                             f"State: {state}, IP Address: {ip_address}")
                print(f"Instance ID: {instance_id}, "
                      f"Type: {instance_type}, "
                      f"State: {state}, IP Address: {ip_address}")
        if not response.get('Reservations', []):
            logging.info(f"No EC2 instances found in region: {region_name}")
            print(f"No EC2 instances found in region: {region_name}")
        print()
    except Exception as e:
        logging.error(f"Unexpected error while "
                      f"processing EC2 instance data: {e}")
        print(f"Unexpected error while processing EC2 instance data: {e}")


def list_instances_by_regions(region, state, tag, csv_file):
    """
    List EC2 instances across specified
    regions with optional filters for state and tags.

    Args:
        region (str): The AWS region to filter instances by
        (e.g., 'us-east-1'). If None, lists instances in all regions.

        state (str): The state to filter instances by
        (e.g., 'running', 'stopped'). If None, lists instances in all states.

        tag (str): The tag to filter instances by in the format 'Key=Value'
        (e.g., 'Environment=Production').
        If None, lists instances regardless of tags.

        csv_file (str): The path to a CSV file to save the instance details.
        If None, instance details will not be saved to a file.
    """
    try:
        session = boto3.session.Session()

        if region:
            regions = [region]
        else:
            # Use session.get_available_regions() instead of
            # describe_regions() - avoids an extra API call and
            # returns all known regions without needing credentials.
            regions = session.get_available_regions("ec2")

        filters = state_filter(state)

        if tag:
            if '=' not in tag:
                logging.error("Tag must be in format 'Key=Value'")
                raise ValueError("Tag must be in format 'Key=Value'")
            tag_key, tag_value = tag.split('=', 1)
            tag_filter = {'Name': f'tag:{tag_key}', 'Values': [tag_value]}
            filters.append(tag_filter)
        if csv_file:
            header = ['Region', 'Instance ID',
                      'Instance Type', 'State', 'IP Address']
            file_path = os.path.join(os.path.dirname(
                        os.path.abspath(__file__)), csv_file)
            with open(file_path, mode='w', newline='') as csv_handle:
                writer = csv.writer(csv_handle)
                writer.writerow(header)

                total_instances = scan_regions(regions, filters, writer)

            logging.info(f"CSV file created at: {file_path}")
            print(f"CSV file created at: {file_path}")
            logging.info(f"Found {total_instances} "
                         f"instances matching the criteria.")
            print(f"Found {total_instances} "
                  f"instances matching the criteria.")
        else:
            writer = None
            total_instances = scan_regions(regions, filters, writer)
            logging.info(f"Found {total_instances} "
                         f"instances matching the criteria.")
            print(f"Found {total_instances} instances matching the criteria.")
    except botocore.exceptions.ClientError as e:
        logging.error(f"AWS ClientError occurred "
                      f"while listing EC2 instances: {e}")
        print(f"AWS ClientError occurred while listing EC2 instances: {e}")
    except Exception as e:
        logging.error(f"Error listing EC2 instances: {e}")
        print(f"Error listing EC2 instances: {e}")


def main():
    parser = argparse.ArgumentParser(
        prog='EC2 Instance Lister',
        description=(
            'A script to list all EC2 instances across all AWS regions.'
        ),
        epilog=(
            'Example usage: python ec2_instance_lister.py'
            '--region us-east-1 --state running --tag Environment=Production'
        )
    )

    parser.add_argument(
        '-r', '--region',
        type=str,
        help='Filter instances by region (e.g., us-east-1)',
        default=None,
    )

    parser.add_argument(
        '-s', '--state',
        type=str,
        help='Filter instances by state (e.g., running, stopped)',
        default=None,
    )

    parser.add_argument(
        '-t', '--tag',
        type=str,
        help='Filter instances by tag (e.g., Environment=Production)',
        default=None,
    )

    parser.add_argument(
        '-lf', '--log_file',
        type=str,
        help='Log file path (default: logs/ec2_instance_lister.log)',
        default='logs/ec2_instance_lister.log'
    )

    parser.add_argument(
        '-csv', '--csv_file',
        type=str,
        help='CSV file path to save instance details (optional)',
        default=None
    )

    args = parser.parse_args()

    # Build log path relative to the script, not the working directory.
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)

    logging.basicConfig(filename=os.path.join
                        (log_dir, os.path.basename(args.log_file)),
                        level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    logging.info("Starting EC2 Instance Lister script.")
    logging.info(f"Arguments: region={args.region}, state={args.state}, "
                 f"tag={args.tag}, csv_file={args.csv_file}")

    list_instances_by_regions(args.region,
                              args.state, args.tag, args.csv_file)


if __name__ == "__main__":
    main()
