import os

from azure.mgmt.cdn import CdnManagementClient
import boto3

from common import get_credentials

dynamodb = boto3.resource('dynamodb')


def handler(event, context):
    subscription_id = os.environ['AzureSubscriptionID']
    client_id = os.environ['AzureClientID']
    secret = os.environ['AzureSecretKey']
    tenant = os.environ['AzureTenantID']
    credentials = get_credentials(
        client=client_id,
        secret_key=secret,
        tenant_id=tenant,
    )
    cdn_client = CdnManagementClient(credentials, subscription_id)
    cdn_profiles = cdn_client.profiles.list()
    for i in cdn_profiles:
        profile_name = ' '.join(i.id.split('/')[-1:])
        group = ''.join(i.id.split('/')[4])
        endpoints_by_profile = cdn_client.endpoints.list_by_profile(
            resource_group_name=group,
            profile_name=profile_name,
        )
        for j in endpoints_by_profile:
            endpoint_hostname = j.host_name
            # origin_hostname = j.origin_host_header
            results = {
                'type': 'cdn',
                'sk': endpoint_hostname,
                'provider': 'azure'
            }
            table = dynamodb.Table(os.environ['DynamoDBTableAssets'])
            table.put_item(
                Item=results
            )
    print('Done')
