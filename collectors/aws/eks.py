import os

import boto3

from common import AWSServiceCollector, AWS_REGIONS_SET

sns = boto3.client('sns')
sts = boto3.client('sts')


class EKSCollector(AWSServiceCollector):
    boto3_service_name = 'eks'

    def _collect_assets(self):
        # first get the list of all clusters:
        max_results = 100
        next_token = ''
        clusters = []
        while True:
            response = self.client.list_clusters(
                maxResults=max_results,
                nextToken=next_token,
            )
            clusters.extend(response['clusters'])

            next_token = response.get('nextToken')
            if next_token is None:
                break
        # get the endpoint for each cluster:
        # TODO: run each iteration of the following loop asynchronously
        for cluster in clusters:
            response = self.client.describe_cluster(cluster)
            endpoint_domain = response['cluster'].get('endpoint')
            if endpoint_domain:
                self.domains.add(endpoint_domain)


def handler_fan_out(event, context):
    """
    Publishes an SNS message for each region from which the assets are to be
    collected.
    """
    eks_regions = AWS_REGIONS_SET - {'ap-northeast-3'}
    for region in eks_regions:
        sns.publish(
            TopicArn=os.environ['SNSTopicCollectAWSEKSARN'],
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

    EKSCollector(client_session).collect()
