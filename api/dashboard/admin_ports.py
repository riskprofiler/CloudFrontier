import decimal
import json
import os
import collections
from boto3.dynamodb.conditions import Key
from utils.dynamodb import DynamoDbWrapper
from utils.decorators import cors_headers

dynamodb = DynamoDbWrapper()

table_name = os.environ['DynamoDBTableCounts']



@cors_headers
def handler(event, context):
    """
    Returns all of the admin ports
    """
    
    admin_ports = dynamodb.query(
        table_name=table_name,
        query=Key('category').eq('admin_port'),
    )
    print(admin_ports)
    if admin_ports:
        admin_ports = sorted(admin_ports, key = lambda i: i['count'], reverse=True)
        
        ports = []
        for items in admin_ports[0:9]:
            port = {
                items['value'] : items['count']
            }
            ports.append(port)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'data': {
                    'admin_ports': ports,
                }
            })
        }
    else:
        return {
            'statusCode': 200,
            'body': json.dumps({
                'data': {
                    'admin_ports': 'NA',
                }
            })
        }