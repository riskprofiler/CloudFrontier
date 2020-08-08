import json
import os
from time import sleep

import boto3
import requests

from utils.dynamodb import DynamoDbWrapper

DELAY_SECONDS_BETWEEN_API_REQUESTS = 15
VIRUSTOTAL_API_KEY = os.environ['APIKeyVirusTotal']
VIRUSTOTAL_API_BASE_URL = 'https://www.virustotal.com/vtapi/v2'

DYNAMODB_TABLE_ASSETS = os.environ['DynamoDBTableAssets']

dynamodb = DynamoDbWrapper()
sqs = boto3.client('sqs')


def handler(event, context):
    """
    Collects the report for a URL given in the SQS ``message`` from
    VirusTotal's API.
    """
    message_json = json.loads(event['Records'][0]['body'])
    asset_type = message_json['type']
    domain_or_ip = message_json[asset_type]
    print(f'Domain or IP: {domain_or_ip}')

    sleep(DELAY_SECONDS_BETWEEN_API_REQUESTS)
    response = requests.get(
        f'{VIRUSTOTAL_API_BASE_URL}/url/report',
        params={
            'apikey': VIRUSTOTAL_API_KEY,
            'resource': domain_or_ip,
            'allinfo': True
        }
    )
    # raise an exception if the status code was 4xx or 5xx:
    response.raise_for_status()
    print('Collected results')

    try:
        result = response.json()
        result['scans']     # check whether `scans` exists in the response
    except (KeyError, json.JSONDecodeError) as e:
        print(f'Could not parse scan results. Error: {e}')
        # no scan results found, request a scan for this URL:
        sleep(DELAY_SECONDS_BETWEEN_API_REQUESTS)
        requests.post(
            f'{VIRUSTOTAL_API_BASE_URL}/url/scan',
            data={
                'apikey': VIRUSTOTAL_API_KEY,
                'url': domain_or_ip,
            }
        )
        print(f'Requested scan')
        sqs.send_message(
            QueueUrl=os.environ['SQSQueueVirusTotalURL'],
            MessageBody=json.dumps(message_json),
        )
        return

    # save the score in DynamoDB:
    dynamodb.update_item(
        table_name=DYNAMODB_TABLE_ASSETS,
        primary_key={
            'type': asset_type,
            'sk': domain_or_ip
        },
        update={
            'vt_score': f'{result["positives"]}/{result["total"]}'
        },
    )
