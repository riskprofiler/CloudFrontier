import json
import os
from time import sleep

import boto3
import requests

from utils.utils import get_timestamp, save_json_in_s3
from utils.dynamodb import DynamoDbWrapper

DELAY_SECONDS_BETWEEN_API_REQUESTS = 1
SHODAN_API_KEY = os.environ['APIKeyShodan']
SHODAN_BASE_URL = 'https://api.shodan.io'
S3_BUCKET_COLLECTORS_STORAGE = os.environ['S3BucketAnalyzers']

dynamodb = DynamoDbWrapper()
sns = boto3.client('sns')


def handler(event, context):
    """
    Gets information from the Shodan API about all services that have been
    found on the given host IP.
    """
    message_body_json = json.loads(event['Records'][0]['body'])
    asset_type = message_body_json['type']
    domain_or_ip = message_body_json[asset_type]

    api_url = f'{SHODAN_BASE_URL}/shodan/host/{domain_or_ip}'
    sleep(DELAY_SECONDS_BETWEEN_API_REQUESTS)
    response = requests.get(api_url, params={
        'key': SHODAN_API_KEY,
    })
    if response.status_code == 404:
        # Shodan doesn't have data for this IP address!
        # TODO: request a scan for this IP using the Shodan API,
        #  and reschedule data collection after 24 hours (or so)
        print('No data available for this IP address')
        return

    # raise an exception if the status code was 4xx or 5xx:
    response.raise_for_status()
    domain_or_ip_results = response.json()
    print('Collected results')

    timestamp = get_timestamp()
    s3_key = f'shodan/{domain_or_ip}_{timestamp}.json'
    save_json_in_s3(domain_or_ip_results, s3_key, S3_BUCKET_COLLECTORS_STORAGE)
    print(f'Saved results in S3 at {s3_key}')

    # signal the analyzers to analyze the collected data:
    sns_topic_arn = os.environ['SNSTopicProcessShodanDataARN']
    sns.publish(
        TopicArn=sns_topic_arn,
        Message=json.dumps({
            'type': asset_type,
            'domain_or_ip': domain_or_ip,
            's3_key': s3_key,
        })
    )
    print(f'Published SNS message to {sns_topic_arn}')
