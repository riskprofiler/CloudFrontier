import os

import boto3

dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')


def handler_fan_out(event, context):
    region_names = ['nyc3', 'sfo2', 'sgp1', 'ams3']
    for region in region_names:
        sns.publish(
            TopicArn=os.environ['SNSTopicCollectDigitalOceanSpacesARN'],
            Message=region,
        )


def handler_regional(event, context):
    region = event['Records'][0]['Sns']['Message']
    session = boto3.session.Session()
    client = session.client(
        's3',
        region_name=region,
        endpoint_url=f'https://{region}.digitaloceanspaces.com',
        aws_access_key_id=os.environ['DigitalOceanAWSAccessKeyID'],
        aws_secret_access_key=os.environ['DigitalOceanAWSAccessSecretKey'],
    )
    response = client.list_buckets()
    spaces = [space['Name'] for space in response['Buckets']]
    for bucket in spaces:
        response = client.get_bucket_acl(
            Bucket=bucket,
        )
        result = {
            'type': 'object_storage',
            'is_public': False,
            'sk': f'{bucket}.{region}.digitaloceanspaces.com',
            'bucket_name': bucket,
            'provider': 'digitalocean',
        }
        for detail in response['Grants']:
            if detail['Grantee']['Type'] == 'Group':
                result['is_public'] = True
        table = dynamodb.Table(os.environ['DynamoDBTableAssets'])
        table.put_item(
            Item=result,
        )
