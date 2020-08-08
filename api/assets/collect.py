import os

import boto3
from utils.decorators import cors_headers

sns = boto3.client('sns')


@cors_headers
def handler(event, context):
    sns.publish(
        TopicArn=os.environ['SNSTopicCollectAssetsARN'],
        Message=' ',    # sending a space since the message cannot be empty
    )

    return {
        'statusCode': 200,
        'body': 'Initialized asset collection',
    }
