import decimal
import json
import os
import collections
from boto3.dynamodb.conditions import Key
from utils.dynamodb import DynamoDbWrapper
from utils.decorators import cors_headers

dynamodb = DynamoDbWrapper()

table_name = os.environ['DynamoDBTableAssets']


@cors_headers
def handler(event, context):
    """
    Returns all of the ip address location data
    """
    # TODO: support pagination to return all "pages" of results
    assets, last_key = dynamodb.query_page(
        table_name=table_name,
        query=Key('type').eq('ip_address'),
    )
    if assets:
        geo_ip = []
        for items in assets:
            if items.get('longitude') and items.get('latitude'):
                ip = {
                    'ip_address': items['sk'],
                    'latitude': items['latitude'],
                    'longitude': items['longitude'],
                }
                geo_ip.append(ip)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'data': {
                    'geo_ip': geo_ip,
                }
            })
        }
    else:
        return {
            'statusCode': 200,
            'body': json.dumps({
                'data': {
                    'geo_ip': 'NA',
                }
            })
        }
