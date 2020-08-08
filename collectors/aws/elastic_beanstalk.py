import os

import boto3

from common import AWSServiceCollector, AWS_REGIONS_SET

sns = boto3.client('sns')
sts = boto3.client('sts')


class ElasticBeanstalkCollector(AWSServiceCollector):
    boto3_service_name = 'elasticbeanstalk'

    def _collect_assets(self):
        # collect Elastic Beanstalk domains and endpoints:
        response = self.client.describe_environments()
        environments = response['Environments']
        for environment in environments:
            # get the endpoint domain:
            endpoint_domain = environment['EndpointURL']
            self.domains.add(endpoint_domain)
            # get custom domain, if any:
            custom_domain = environment.get('CNAME')
            if custom_domain:
                self.domains.add(custom_domain)


def handler_fan_out(event, context):
    """
    Publishes an SNS message for each region from which the assets are to be
    collected.
    """
    elasticbeanstalk_regions = AWS_REGIONS_SET
    for region in elasticbeanstalk_regions:
        sns.publish(
            TopicArn=os.environ['SNSTopicCollectAWSElasticBeanstalkARN'],
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

    ElasticBeanstalkCollector(client_session).collect()
