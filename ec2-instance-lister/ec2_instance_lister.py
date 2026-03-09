import boto3
import botocore.exceptions
import logging


def list_ec2_instances_by_regions():
    try:
        # Create an EC2 client
        ec2_client = boto3.client('ec2')

        # Retrieve the list of available regions
        regions_response = ec2_client.describe_regions()
        regions = [region['RegionName']
                   for region in regions_response['Regions']]

        # Iterate through each region and list EC2 instances
        for region in regions:
            print(f"Listing EC2 instances in region: {region}")
            regional_ec2_client = boto3.client('ec2', region_name=region)
            response = regional_ec2_client.describe_instances()
            list_ec2_instances(response)
    except botocore.exceptions.ClientError:
        logging.error("AWS ClientError occurred while listing EC2 instances.")
        print("AWS ClientError occurred while listing EC2 instances.")
    except Exception as e:
        logging.error(f"Error listing EC2 instances: {e}")
        print(f"Error listing EC2 instances: {e}")


def list_ec2_instances(response):
    try:
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                instance_type = instance['InstanceType']
                state = instance['State']['Name']
                ip_address = instance.get('PublicIpAddress', 'N/A')
                print(f"Instance ID: {instance_id}, "
                      f"Type: {instance_type}, "
                      f"State: {state}, IP Address: {ip_address}")
        print("\n")
    except KeyError as e:
        logging.error(f"KeyError occurred while "
                      f"processing EC2 instance data: {e}")
        print(f"KeyError occurred while processing EC2 instance data: {e}")


def main():
    logging.basicConfig(filename='ec2_instance_lister.log', level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("EC2 instance listing completed.")

    list_ec2_instances_by_regions()


if __name__ == "__main__":
    main()
