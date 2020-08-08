import json
import os

import boto3

from common import AWSServiceCollector, AWS_REGIONS_SET

sns = boto3.client('sns')
sts = boto3.client('sts')


class ElasticsearchCollector(AWSServiceCollector):
    boto3_service_name = 'es'

    def _collect_assets(self):
        # get Elasticsearch endpoints:
        response = self.client.list_domain_names()
        domains = response['DomainNames']
        for domain in domains:
            response = self.client.describe_elasticsearch_domain(
                DomainName=domain['DomainName'],
            )
            domain_endpoint = response['DomainStatus'].get('Endpoint')
            if domain_endpoint:
                self.data_store_endpoints.add(domain_endpoint)

                # check for public access:
                is_public = False
                vpc_options = response['DomainStatus'].get('VPCOptions')
                if vpc_options is None:
                    # vpc is not used, check access policies:
                    access_policy = response['DomainStatus']['AccessPolicies']
                    try:
                        access_policy_json = json.loads(access_policy)
                        for statement in access_policy_json['Statement']:
                            is_allowed = statement['Effect'] == 'Allow'
                            to_all = statement['Principal'] == {'AWS': '*'}
                            if is_allowed and to_all:
                                condition = statement.get('Condition')
                                if condition is None:
                                    is_public = True
                                else:
                                    # check if condition allows open access:
                                    try:
                                        ip_condition = condition['IpAddress']
                                        if ip_condition['aws:SourceIp'] == '*':
                                            is_public = True
                                    except KeyError:
                                        pass
                    except json.JSONDecodeError:
                        # access policy is empty
                        is_public = True
                self.data_store_endpoint_attributes[domain_endpoint] = {
                    'is_public': is_public,
                }


def handler_fan_out(event, context):
    """
    Publishes an SNS message for each region from which the assets are to be
    collected.
    """
    elasticsearch_regions = AWS_REGIONS_SET - {'ap-northeast-3'}
    for region in elasticsearch_regions:
        sns.publish(
            TopicArn=os.environ['SNSTopicCollectAWSElasticsearchARN'],
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

    ElasticsearchCollector(client_session).collect()
