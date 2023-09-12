import boto3
import json

def lambda_handler(event, context):

    # Get the specific EC2 instance.
    ec2_client = boto3.client('ec2')
    
    # Assume compliant by default
    compliance_status = "COMPLIANT"  
    compliance_status_s3 = "COMPLIANT"  
    
    # Extract the configuration item from the invokingEvent
    config = json.loads(event['invokingEvent'])
    print("Printing the config item ", config)
    
    
    if config['configurationItem']['resourceType'] == 'AWS::S3::Bucket':
        configuration_item = config["configurationItem"]
        print("Printing the configuration_item ", configuration_item)
        
        supplementaryConfiguration_item = configuration_item["supplementaryConfiguration"]
        print("Printing the supplementaryConfiguration_item ", supplementaryConfiguration_item)
        
        if not supplementaryConfiguration_item["PublicAccessBlockConfiguration"]["blockPublicPolicy"]:
            compliance_status_s3 = "NON_COMPLIANT"
            
        evaluation = {
            'ComplianceResourceType': 'AWS::S3::Bucket',
            'ComplianceResourceId': configuration_item["resourceId"],
            'ComplianceType': compliance_status_s3,
            'Annotation': 'Public Access for S3 bucket is not blocked.',
            'OrderingTimestamp': configuration_item["configurationItemCaptureTime"]
        }
    
        print("Printing the evaluation ", evaluation)
    
        config_client = boto3.client('config')
    
        response = config_client.put_evaluations(
            Evaluations=[evaluation],
            ResultToken=event['resultToken']
        )
    else:
        # Extract the instanceId
        instance_id = configuration_item['configuration']['instanceId']
        print("Printing the instance_id ", instance_id)
    
        # Get complete Instance details
        instance = ec2_client.describe_instances(InstanceIds=[instance_id])['Reservations'][0]['Instances'][0]
        print("Printing the complete instance details ", instance)
    
        # Check if the specific EC2 instance has Cloud Trail logging enabled.
    
        if not instance['Monitoring']['State'] == "enabled":
            compliance_status = "NON_COMPLIANT"

        evaluation = {
            'ComplianceResourceType': 'AWS::EC2::Instance',
            'ComplianceResourceId': instance_id,
            'ComplianceType': compliance_status,
            'Annotation': 'Detailed monitoring is not enabled.',
            'OrderingTimestamp': config['notificationCreationTime']
        }
    
        print("Printing the evaluation ", evaluation)
    
        config_client = boto3.client('config')
    
        response = config_client.put_evaluations(
            Evaluations=[evaluation],
            ResultToken=event['resultToken']
        )
    
    
    print("Printing the response which sending to the config ", response)
    
    return response
