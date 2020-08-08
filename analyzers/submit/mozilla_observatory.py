import json
import os
from time import sleep

import boto3
import requests

from utils.dynamodb import DynamoDbWrapper

DELAY_SECONDS_BETWEEN_API_REQUESTS = 1
API_BASE_URL = 'https://http-observatory.security.mozilla.org/api/v1/analyze'
DYNAMODB_TABLE_ASSETS = os.environ['DynamoDBTableAssets']

dynamodb = DynamoDbWrapper()
sqs = boto3.client('sqs')


def handler(event, context):
    """
    Collects the report for a domain given in the SQS ``message`` from
    Mozilla Observatory's API.
    """
    message_json = json.loads(event['Records'][0]['body'])

    asset_type = message_json['type']
    domain_or_ip = message_json[asset_type]
    print(f'Domain or IP: {domain_or_ip}')
    scan_or_report = message_json.get('scan_or_report', 'scan')

    if scan_or_report == 'scan':
        api_url = f'{API_BASE_URL}?host={domain_or_ip}'
        post_data = {'hidden': 'true', 'rescan': 'true'}
        sleep(DELAY_SECONDS_BETWEEN_API_REQUESTS)
        requests.post(api_url, data=post_data)
        print('Requested scan')
        message_json['scan_or_report'] = 'report'
        sqs.send_message(
            QueueUrl=os.environ['SQSQueueObservatoryURL'],
            MessageBody=json.dumps(message_json),
        )
        return

    sleep(DELAY_SECONDS_BETWEEN_API_REQUESTS)
    response = requests.get(API_BASE_URL, params={
        'host': domain_or_ip,
    })
    # raise an exception if the status code was 4xx or 5xx:
    response.raise_for_status()
    print('Collected results')

    result = response.json()
    print(result)
    scan_state = result['state']
    if scan_state in ['PENDING', 'RUNNING']:
        # schedule getting the report later
        sqs.send_message(
            QueueUrl=os.environ['SQSQueueObservatoryURL'],
            MessageBody=json.dumps(message_json),
        )
        print('Queued the report collection')
        return
    elif scan_state == 'FAILED':
        observatory_grade = 'NA'
    else:
        observatory_grade = result['grade']

    dynamodb.update_item(
        table_name=DYNAMODB_TABLE_ASSETS,
        primary_key={
            'type': asset_type,
            'sk': domain_or_ip
        },
        update={
            'observatory_grade': observatory_grade
        },
    )
