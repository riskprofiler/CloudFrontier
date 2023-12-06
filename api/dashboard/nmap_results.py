import json
import os

from boto3.dynamodb.conditions import Key

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
        query=Key('category').eq('nmap_result'),
    )

    if nmap_results:
        scan_details = []
        for results in nmap_results:
            host = json.loads(results['value'])['hosts'][0]
            for ports in host['ports']:
                for script_output in ports['scripts']:
                    item = {
                    'host': host,
                    'port': ports['id'],
                    'protocol': ports['protocol'],
                    'service': ports['service'],
                    'script': script_output['output']
                    }
                    scan_details.append(item)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'data': {
                    'nmap_results': scan_details,
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
