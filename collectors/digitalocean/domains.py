import json
import os

import digitalocean
import boto3

DIGITALOCEAN_TOKEN = os.environ['DigitalOceanToken']

dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')


def handler(event, context):
    manager = digitalocean.Manager(token=DIGITALOCEAN_TOKEN)
    domains = manager.get_all_domains()
    for domain in domains:
        results = {
            'type': 'domain',
            'sk': domain.name,
            'provider': 'digitalocean',
        }
        table = dynamodb.Table(os.environ['DynamoDBTableAssets'])
        table.put_item(
            Item=results,
        )
        sns.publish(
            TopicArn=os.environ['SNSTopicAnalyzeDomainARN'],
            Message=json.dumps({
                'type': 'domain',
                'domain': domain.name,
            }),
        )
