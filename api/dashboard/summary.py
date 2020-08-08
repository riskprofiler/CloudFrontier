import json
import os

from boto3.dynamodb.conditions import Key

from utils.dynamodb import DynamoDbWrapper
from utils.decorators import cors_headers

dynamodb = DynamoDbWrapper()

DYNAMODB_TABLE_COUNTS = os.environ['DynamoDBTableCounts']


@cors_headers
def handler(event, context):
    """
    Returns all of the Dashboard Data
    """
    dashboard = []

    ports = dynamodb.query(
        table_name=DYNAMODB_TABLE_COUNTS,
        query=Key('category').eq('summary'),
    )

    for items in ports:
        vuln = {
            items['value']: items['count']
        }
        dashboard.append(vuln)

    ips = dynamodb.query(
        table_name=DYNAMODB_TABLE_COUNTS,
        query=Key('category').eq('asset') & Key('value').eq('ip_address'),
    )
    for items in ips:
        ip = {
            items['value']: items['count']
        }
        dashboard.append(ip)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'data': {
                'dashboard': dashboard,
            }
        })
    }
