import boto3

def lambda_handler(event, context):
    # Create AWS clients for EC2 and EBS
    ec2_client = boto3.client('ec2')
    ebs_client = boto3.client('ec2')
    
    # Get all EBS snapshots owned by the same account ('self')
    response = ebs_client.describe_snapshots(OwnerIds=['self'])
    snapshots = response['Snapshots']
    
    # Get a list of active EC2 instances (running and stopped)
    response = ec2_client.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running', 'stopped']}])
    instances = []
    for reservation in response['Reservations']:
        instances.extend(reservation['Instances'])
    
    # Extract the volume ID from each instance
    active_volumes = set()
    for instance in instances:
        for block_device in instance['BlockDeviceMappings']:
            if 'Ebs' in block_device:
                active_volumes.add(block_device['Ebs']['VolumeId'])
    
    # Check each snapshot and delete stale snapshots (not associated with an active volume)
    for snapshot in snapshots:
        volume_id = snapshot['VolumeId']
        if volume_id not in active_volumes:
            print(f"Deleting stale snapshot with ID: {snapshot['SnapshotId']} as its associated volume was not found.")
            ebs_client.delete_snapshot(SnapshotId=snapshot['SnapshotId'])

    return {
        'statusCode': 200,
        'body': 'Snapshot cleanup complete.'
    }
