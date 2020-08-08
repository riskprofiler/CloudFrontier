import os

from azure.mgmt.storage import StorageManagementClient
from azure.storage.blob import BlockBlobService
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
    blob_client = StorageManagementClient(credentials, subscription_id)
    storage_accounts = blob_client.storage_accounts.list()
    for account in storage_accounts:
        group = ''.join(account.id.split('/')[4])
        storage_keys = blob_client.storage_accounts.list_keys(group, account.name)
        storage_keys = {v.key_name: v.value for v in storage_keys.keys}
        key1 = storage_keys['key1']
        block_blob_service = BlockBlobService(account_name=account.name, account_key=key1)
        containers = block_blob_service.list_containers()
        for container in containers:
            access = container.properties.public_access
            public_access = not(access == 'None')
            result = {
                'type': 'object_storage',
                'sk': container.name,
                'provider': 'azure',
                'is_public': public_access,
            }
            table = dynamodb.Table(os.environ['DynamoDBTableAssets'])
            table.put_item(
                Item=result,
            )
    print('Done')
