import json
import os

import digitalocean
import boto3

DIGITALOCEAN_TOKEN = os.environ['DigitalOceanToken']

dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')


def handler(event, context):
    manager = digitalocean.Manager(token=DIGITALOCEAN_TOKEN)
    floating_ips = manager.get_all_floating_ips()
    for floating_ip in floating_ips:
        results = {
            'type': 'ip_address',
            'sk': floating_ip.ip,
            'provider': 'digitalocean',
        }
        table = dynamodb.Table(os.environ['DynamoDBTableAssets'])
        table.put_item(
            Item=results,
        )
        sns.publish(
            TopicArn=os.environ['SNSTopicAnalyzeIPARN'],
            Message=json.dumps({
                'type': 'ip_address',
                'ip_address': floating_ip.ip,
            }),
        )
