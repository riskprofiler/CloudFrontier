import os

import boto3

from common import AWSServiceCollector, AWS_REGIONS_SET

sns = boto3.client('sns')
sts = boto3.client('sts')


class ElasticacheCollector(AWSServiceCollector):
    boto3_service_name = 'elasticache'

    def _collect_assets(self):
        max_records = 100
        marker = ''
        while True:
            response = self.client.describe_cache_clusters(
                MaxRecords=max_records,
                Marker=marker,
            )
            clusters = response['CacheClusters']
            for cluster in clusters:
                # get cache nodes' endpoints:
                cluster_nodes = cluster.get('Nodes')
                for node in cluster_nodes:
                    endpoint_domain = node['Endpoint']['Address']
                    self.data_store_endpoints.add(endpoint_domain)
                # get configuration endpoint, if any (for Memcached clusters):
                configuration_endpoint = cluster.get('ConfigurationEndpoint')
                if configuration_endpoint:
                    endpoint_domain = configuration_endpoint['Address']
                    self.data_store_endpoints.add(endpoint_domain)

            # check if more pages of results are to be fetched:
            marker = response.get('Marker')
            if marker is None:
                break


def handler_fan_out(event, context):
    """
    Publishes an SNS message for each region from which the assets are to be
    collected.
    """
    elasticache_regions = AWS_REGIONS_SET
    for region in elasticache_regions:
        sns.publish(
            TopicArn=os.environ['SNSTopicCollectAWSElasticacheARN'],
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

    ElasticacheCollector(client_session).collect()
