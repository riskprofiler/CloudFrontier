import json
import os

import digitalocean
import boto3

DIGITALOCEAN_TOKEN = os.environ['DigitalOceanToken']

dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')


def handler(event, context):
    manager = digitalocean.Manager(token=DIGITALOCEAN_TOKEN)
    load_balancers = manager.get_all_load_balancers()
    for load_balancer in load_balancers:
        ip_address = load_balancer.ip
        results = {
            'type': 'ip_address',
            'sk': ip_address,
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
                'ip_address': ip_address,
            }),
        )
