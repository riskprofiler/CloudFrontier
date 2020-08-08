import os

import boto3

from common import AWSServiceCollector, AWS_REGIONS_SET

sns = boto3.client('sns')
sts = boto3.client('sts')


class ELBCollector(AWSServiceCollector):
    boto3_service_name = 'elb'

    def _collect_assets(self):
        # collect domains of ELB load balancers:
        page_size = 400
        marker = ''
        while True:
            response = self.client.describe_load_balancers(
                PageSize=page_size,
                Marker=marker,
            )
            load_balancers = response['LoadBalancerDescriptions']
            for load_balancer in load_balancers:
                # get the domain name:
                domain = load_balancer['DNSName']
                self.domains.add(domain)
                # get custom domain, if any:
                custom_domain = load_balancer.get('CanonicalHostedZoneName')
                if custom_domain:
                    self.domains.add(custom_domain)

            # check if more pages of results are to be fetched:
            marker = response.get('NextMarker')
            if marker is None:
                break


class ELBv2Collector(AWSServiceCollector):
    boto3_service_name = 'elbv2'

    def _collect_assets(self):
        # collect domains of ELB load balancers:
        page_size = 400
        marker = ''
        while True:
            response = self.client.describe_load_balancers(
                PageSize=page_size,
                Marker=marker,
            )
            load_balancers = response['LoadBalancers']
            for load_balancer in load_balancers:
                # get the domain name:
                domain = load_balancer['DNSName']
                self.domains.add(domain)
                # get IP addresses for various availability zones, if any
                # (for network load balancers):
                availability_zones = load_balancer.get('AvailabilityZones', [])
                for zone in availability_zones:
                    load_balancer_addresses = zone['LoadBalancerAddresses']
                    for address in load_balancer_addresses:
                        public_ip_address = address.get('IpAddress')
                        if public_ip_address:
                            self.ip_addresses.add(public_ip_address)

            # check if more pages of results are to be fetched:
            marker = response.get('NextMarker')
            if marker is None:
                break


def handler_fan_out(event, context):
    """
    Publishes an SNS message for each region from which the assets are to be
    collected.
    """
    elb_regions = AWS_REGIONS_SET
    for region in elb_regions:
        sns.publish(
            TopicArn=os.environ['SNSTopicCollectAWSELBARN'],
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

    ELBCollector(client_session).collect()


def handler_v2_regional(event, context):
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

    ELBv2Collector(client_session).collect()
