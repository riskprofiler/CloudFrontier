import os

import boto3

sns = boto3.client('sns')

dynamodb = boto3.resource('dynamodb')


def truncate_dynamodb_table(table_name: str, key_attributes: list):
    table = dynamodb.Table(table_name)
    kwargs = {
        'ProjectionExpression': ', '.join([f'#{a}_key' for a in key_attributes]),
        'ExpressionAttributeNames': {f'#{a}_key': a for a in key_attributes},
    }
    scan = {}
    with table.batch_writer() as batch:
        while scan == {} or 'LastEvaluatedKey' in scan:
            if scan.get('LastEvaluatedKey'):
                kwargs['ExclusiveStartKey'] = scan['LastEvaluatedKey']
            scan = table.scan(**kwargs)

            for item in scan['Items']:
                batch.delete_item(Key={a: item[a] for a in key_attributes})


def handler(event, context):
    # delete all items from the `Assets` and `Counts` tables:
    tables_and_key_attributes = [
        (os.environ['DynamoDBTableAssets'], ['type', 'sk']),
        (os.environ['DynamoDBTableCounts'], ['category', 'value']),
    ]
    for table_name, key_attributes in tables_and_key_attributes:
        truncate_dynamodb_table(table_name, key_attributes)
        print(f'Deleted all items from the {table_name} table')

    # publish SNS messages to collect assets from various cloud providers:
    sns_topic_arns = [
        os.environ['SNSTopicCollectAWSARN'],
        os.environ['SNSTopicCollectGCPARN'],
        os.environ['SNSTopicCollectAzureARN'],
        os.environ['SNSTopicCollectDigitalOceanARN'],
        os.environ['SNSTopicCollectOracleARN'],
    ]
    for topic_arn in sns_topic_arns:
        sns.publish(
            TopicArn=topic_arn,
            Message=' ',    # sending a space since the message cannot be empty
        )
        print(f'Published message to SNS topic {topic_arn}')
