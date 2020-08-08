import os

import boto3

from common import AWSServiceCollector, AWS_REGIONS_SET

sns = boto3.client('sns')
sts = boto3.client('sts')


class RDSCollector(AWSServiceCollector):
    boto3_service_name = 'rds'

    def _collect_assets(self):
        # collect endpoints and domains of RDS instances:
        max_records = 100
        marker = ''
        while True:
            response = self.client.describe_db_instances(
                MaxRecords=max_records,
                Marker=marker,
            )
            instances = response['DBInstances']
            for instance in instances:
                endpoint = instance['Endpoint'].get('Address')
                if endpoint:
                    self.data_store_endpoints.add(endpoint)
                # get Active Directory Domain membership records associated
                # with the DB instance:
                for domain_membership in instance.get('DomainMemberships', []):
                    domain = domain_membership['Domain']
                    self.domains.add(domain)
                # get the listener connection endpoint for "SQL Server Always
                # On":
                listener_endpoint = instance.get('ListenerEndpoint', {}).get('Address')
                if listener_endpoint:
                    self.data_store_endpoints.add(listener_endpoint)

            # check if more pages of results are to be fetched:
            marker = response.get('Marker')
            if marker is None:
                break

        # get Aurora DB clusters' endpoints:
        max_records = 100
        marker = ''
        while True:
            response = self.client.describe_db_clusters(
                MaxRecords=max_records,
                Marker=marker,
            )
            clusters = response['DBClusters']
            for cluster in clusters:
                # get connection endpoint:
                connection_endpoint = instance['Endpoint']
                self.data_store_endpoints.add(connection_endpoint)
                # get reader endpoint:
                reader_endpoint = instance['ReaderEndpoint']
                self.data_store_endpoints.add(reader_endpoint)
                # get custom endpoints, if any:
                custom_endpoints = instance.get('CustomEndpoints', [])
                for endpoint in custom_endpoints:
                    self.data_store_endpoints.add(endpoint)
                # get Active Directory Domain membership records associated
                # with the DB instance:
                for domain_membership in instance.get('DomainMemberships', []):
                    domain = domain_membership['Domain']
                    self.domains.add(domain)

            # check if more pages of results are to be fetched:
            marker = response.get('Marker')
            if marker is None:
                break


def handler_fan_out(event, context):
    """
    Publishes an SNS message for each region from which the assets are to be
    collected.
    """
    rds_regions = AWS_REGIONS_SET
    for region in rds_regions:
        sns.publish(
            TopicArn=os.environ['SNSTopicCollectAWSRDSARN'],
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

    RDSCollector(client_session).collect()
