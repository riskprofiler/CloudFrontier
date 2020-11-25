import json
import os
import boto3

from boto3.dynamodb.conditions import Key

from utils.decorators import cors_headers
from utils.dynamodb import DynamoDbWrapper

dynamodb = DynamoDbWrapper()

table_name = os.environ['DynamoDBTableCounts']

@cors_headers
def handler(event, context):
    """
    Returns all of the Vulnerabilities
    """
    vulnerabilities = dynamodb.query(
        table_name=table_name,
        query=Key('category').eq('vuln'),
    )
    if vulnerabilities:
        vulnerabilities = sorted(vulnerabilities, key = lambda i: i['count'], reverse=True)
        vulns = []
        for items in vulnerabilities[0:9]:
            vuln = {
                items['value'] : items['count']
            }
            vulns.append(vuln)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'data': {
                    'vulnerabilities': vulns,
                }
            })
        }
    else:
        return {
            'statusCode': 200,
            'body': json.dumps({
                'data': {
                    'vulnerabilities': 'NA',
                }
            })
        }