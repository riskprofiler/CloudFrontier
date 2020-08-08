import json
import os

from boto3.dynamodb.conditions import Key
from operator import itemgetter

from utils.dynamodb import DynamoDbWrapper
from utils.decorators import cors_headers

dynamodb = DynamoDbWrapper()

table_name = os.environ['DynamoDBTableCounts']


@cors_headers
def handler(event, context):
    """
    Returns all of the Common Ports
    """
    common_ports = dynamodb.query(
        table_name=table_name,
        query=Key('category').eq('common_port'),
    )

    if common_ports:
        common_ports = sorted(common_ports, key=lambda i: i['count'], reverse=True)
        ports = []
        for items in common_ports[0:9]:
            port = {
                items['value']: items['count']
            }
            ports.append(port)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'data': {
                    'common_ports': ports,
                }
            })
        }
    else:
        return {
            'statusCode': 200,
            'body': json.dumps({
                'data': {
                    'common_ports': 'NA',
                }
            })
        }
