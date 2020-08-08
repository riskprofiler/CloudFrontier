import os

import boto3

from common import AWSServiceCollector, AWS_REGIONS_SET

sns = boto3.client('sns')
sts = boto3.client('sts')


class EC2Collector(AWSServiceCollector):
    boto3_service_name = 'ec2'

    def _collect_assets(self):
        # collect IP addresses and domains of EC2 instances:
        max_results = 1000
        next_token = ''
        while True:
            response = self.client.describe_instances(
                MaxResults=max_results,
                NextToken=next_token,
            )
            reservations = response['Reservations']
            for reservation in reservations:
                for instance in reservation['Instances']:
                    public_dns_name = instance['PublicDnsName']
                    if public_dns_name:
                        self.domains.add(public_dns_name)
                    public_ip_address = instance['PublicIpAddress']
                    if public_ip_address:
                        self.ip_addresses.add(public_ip_address)

            # check if more pages of results are to be fetched:
            next_token = response.get('NextToken')
            if next_token is None:
                break

        # collect elastic IPs:
        response = self.client.describe_addresses()
        for address in response['Addresses']:
            self.ip_addresses.add(address['PublicIp'])


def handler_fan_out(event, context):
    """
    Publishes an SNS message for each region from which the assets are to be
    collected.
    """
    ec2_regions = AWS_REGIONS_SET
    for region in ec2_regions:
        sns.publish(
            TopicArn=os.environ['SNSTopicCollectAWSEC2ARN'],
            Message=region,
        )


def handler_regional(event, context):
    region = event['Records'][0]['Sns']['Message']

    response = sts.assume_role(
        RoleArn=os.environ['AWSIAMRoleARN'],
        RoleSessionName='CloudFrontierAssetCollector',
        # ExternalId='...',
    )
    print(f'Assumed IAM role')

    credentials = response['Credentials']
    client_session = boto3.Session(
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken'],
        region_name=region,
    )
    print(f'Created session')

    EC2Collector(client_session).collect()
