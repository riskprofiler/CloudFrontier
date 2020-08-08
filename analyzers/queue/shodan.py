import os

import boto3

sqs = boto3.client('sqs')


def handler(event, context):
    """
    This Lambda exists as AWS does not support subscribing an SQS FIFO queue
    to an SNS topic. Once this feature is available, this Lambda can be
    removed.
    """
    message = event['Records'][0]['Sns']['Message']
    print(f'Message: {message}')

    sqs.send_message(
        QueueUrl=os.environ['SQSQueueShodanURL'],
        MessageBody=message,
    )
