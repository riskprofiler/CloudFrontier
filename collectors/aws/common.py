import json
import os

import boto3

from utils.dynamodb import DynamoDbWrapper

dynamodb = DynamoDbWrapper()
sns = boto3.client('sns')

AWS_REGIONS_SET = {
    'af-south-1',
    'ap-east-1',
    'ap-northeast-1',
    'ap-northeast-2',
    'ap-northeast-3',
    'ap-south-1',
    'ap-southeast-1',
    'ap-southeast-2',
    'ca-central-1',
    'eu-central-1',
    'eu-north-1',
    'eu-south-1',
    'eu-west-1',
    'eu-west-2',
    'eu-west-3',
    'me-south-1',
    'sa-east-1',
    'us-east-1',
    'us-east-2',
    'us-west-1',
    'us-west-2',
}


class AWSServiceCollector:
    boto3_service_name = None

    def __init__(self, session: boto3.Session):
        self.client = session.client(self.boto3_service_name)
        print(f'Connected with {self.boto3_service_name} client')
        # asset sets:
        self.domains = set()
        self.ip_addresses = set()
        self.object_storage_endpoints = set()
        self.data_store_endpoints = set()
        self.api_root_endpoints = set()
        self.cdn_endpoints = set()
        # additional asset attributes:
        self.object_storage_endpoint_attributes = {}
        self.data_store_endpoint_attributes = {}
        self.api_root_endpoint_attributes = {}

    def collect(self):
        self._collect_assets()
        print(f'Collected '
              f'{len(self.domains)} domains, '
              f'{len(self.ip_addresses)} IPs, '
              f'{len(self.object_storage_endpoints)} object storages, '
              f'{len(self.data_store_endpoints)} data stores, '
              f'{len(self.api_root_endpoints)} APIs, '
              f'{len(self.cdn_endpoints)} CDNs.')
        self._save_assets()

    def _collect_assets(self):
        raise NotImplementedError   # implementation depends on the service

    def _save_assets(self):
        assets = []
        for ip_address in self.ip_addresses:
            assets.append({
                'type': 'ip_address',
                'sk': ip_address,
                'provider': 'aws',
            })
            sns.publish(
                TopicArn=os.environ['SNSTopicAnalyzeIPARN'],
                Message=json.dumps({
                    'type': 'ip_address',
                    'ip_address': ip_address,
                }),
            )
        for domain in self.domains:
            assets.append({
                'type': 'domain',
                'sk': domain,
                'provider': 'aws',
            })
            sns.publish(
                TopicArn=os.environ['SNSTopicAnalyzeDomainARN'],
                Message=json.dumps({
                    'type': 'domain',
                    'domain': domain,
                }),
            )
        for object_storage_endpoint in self.object_storage_endpoints:
            assets.append({
                'type': 'object_storage',
                'sk': object_storage_endpoint,
                'provider': 'aws',
                **self.object_storage_endpoint_attributes.get(object_storage_endpoint, {}),
            })
        for data_store_endpoint in self.data_store_endpoints:
            assets.append({
                'type': 'data_store',
                'sk': data_store_endpoint,
                'provider': 'aws',
                **self.data_store_endpoint_attributes.get(data_store_endpoint, {}),
            })
        for api_root_endpoint in self.api_root_endpoints:
            assets.append({
                'type': 'api_endpoint',
                'sk': api_root_endpoint,
                'provider': 'aws',
                **self.api_root_endpoint_attributes.get(api_root_endpoint, {}),
            })
        for cdn_endpoint in self.cdn_endpoints:
            assets.append({
                'type': 'cdn',
                'sk': cdn_endpoint,
                'provider': 'aws',
            })

        if assets:
            dynamodb.batch_writer(
                table_name=os.environ['DynamoDBTableAssets'],
                data_list=assets,
            )
