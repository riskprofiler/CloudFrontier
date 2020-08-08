import os

import boto3

from common import AWSServiceCollector, AWS_REGIONS_SET

sns = boto3.client('sns')
sts = boto3.client('sts')


class APIGatewayRESTCollector(AWSServiceCollector):
    boto3_service_name = 'apigateway'

    def _collect_assets(self):
        # get REST APIs:
        rest_apis = []
        kwargs = {
            'limit': 500,
        }
        position = ''
        while True:
            if position:
                kwargs['position'] = position
            response = self.client.get_rest_apis(**kwargs)
            rest_apis.extend(response['items'])

            position = response.get('position')
            if not position:
                break

        # check authorizers and get the stages for each REST API:
        for rest_api in rest_apis:
            rest_api_id = rest_api['id']

            response = self.client.get_authorizers(restApiId=rest_api_id)
            if len(response['items']) == 0:
                is_public = True
            else:
                is_public = False

            # get the stages using which API root endpoints will be saved:
            response = self.client.get_stages(restApiId=rest_api_id)
            for stage in response['item']:
                stage_name = stage['stageName']
                endpoint = f'https://{rest_api_id}.execute-api.{self.client.meta.region_name}.amazonaws.com/{stage_name}'
                self.api_root_endpoints.add(endpoint)
                self.api_root_endpoint_attributes[endpoint] = {
                    'is_public': is_public,
                }

        # get custom domains:
        kwargs = {
            'limit': 500,
        }
        position = ''
        while True:
            if position:
                kwargs['position'] = position
            response = self.client.get_domain_names(**kwargs)
            for item in response['items']:
                self.domains.add(item['domainName'])
                self.domains.add(item['distributionDomainName'])
                if item.get('regionalDomainName'):
                    self.domains.add(item['regionalDomainName'])

            position = response.get('position')
            if not position:
                break


def handler_fan_out(event, context):
    """
    Publishes an SNS message for each region from which the assets are to be
    collected.
    """
    api_gateway_regions = AWS_REGIONS_SET - {'ap-northeast-3'}
    for region in api_gateway_regions:
        sns.publish(
            TopicArn=os.environ['SNSTopicCollectAWSAPIGatewayARN'],
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

    APIGatewayRESTCollector(client_session).collect()
