import boto3

def delete_unattached_volumes():
    # Create an AWS client for EC2
    ec2_client = boto3.client('ec2')
    
    # Get a list of all EBS volumes in the account
    response = ec2_client.describe_volumes()
    volumes = response['Volumes']
    
    # Filter out volumes that are not attached to any EC2 instance
    unattached_volumes = [volume for volume in volumes if 'Attachments' not in volume or len(volume['Attachments']) == 0]
    
    # Delete unattached volumes
    for volume in unattached_volumes:
        volume_id = volume['VolumeId']
        print(f"Deleting unattached volume with ID: {volume_id} as its associated ec2 instance was not found.")
        ec2_client.delete_volume(VolumeId=volume_id)

def lambda_handler(event, context):
    # Call the delete_unattached_volumes function
    delete_unattached_volumes()
    
    return {
        'statusCode': 200,
        'body': 'Unattached EBS volumes cleanup complete.'
    }
