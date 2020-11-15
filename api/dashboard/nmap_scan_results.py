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
    Returns the Nmap scan results
    """
    nmap_results = dynamodb.query(
        table_name=table_name,
        query=Key('category').eq('nmap_results'),
    )

    if nmap_results:
        open_ports = sorted(nmap_results['Hosts'][0]['Ports'], key=lambda i: i['State'].lower() == 'open')
        ports_details = []
        for items in open_ports:
            port = {
                items['ID']: items['Protocol']
            }
            ports_details.append(port)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'data': {
                    'nmap_results': ports_details,
                }
            })
        }
    else:
        return {
            'statusCode': 200,
            'body': json.dumps({
                'data': {
                    'nmap_results': 'NA',
                }
            })
        }
