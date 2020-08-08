import json
import os
import re

import boto3
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient

from common import get_credentials

dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')


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
    compute_client = ComputeManagementClient(credentials, subscription_id)
    network_client = NetworkManagementClient(credentials, subscription_id)
    v_machines = compute_client.virtual_machines.list_all()
    for vm in v_machines:
        network_interface = vm.network_profile.network_interfaces
        for interface in network_interface:
            machine_name = ' '.join(interface.id.split('/')[-1:])
            group = ''.join(interface.id.split('/')[4])
            res = [re.findall(r'(\w+?)(\d+)', machine_name)[0]]
            vm_ip_no = str(res[0][1])
            vm_ip = machine_name.replace(vm_ip_no, '-ip')
            public_ip = network_client.public_ip_addresses.get(group, vm_ip).ip_address
            if public_ip is not None:
                results = {
                    'type': 'ip_address',
                    'sk': public_ip,
                    'provider': 'azure'
                }
                table = dynamodb.Table(os.environ['DynamoDBTableAssets'])
                table.put_item(
                    Item=results
                )
                sns.publish(
                    TopicArn=os.environ['SNSTopicAnalyzeIPARN'],
                    Message=json.dumps({
                        'type': 'ip_address',
                        'ip_address': public_ip,
                    }),
                )
    print('Done')
