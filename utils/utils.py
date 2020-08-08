import json
import os
import time
import uuid

import boto3
from botocore.exceptions import ClientError

DEFAULT_S3_BUCKET = os.environ.get('S3BucketAnalyzers')

s3 = boto3.client('s3')


def get_timestamp() -> int:
    return int(time.time() * 1000)     # include milliseconds in the timestamp


def get_uuid5(*names) -> str:
    """
    Returns a UUIDv5 string using the DNS namespace and by combining the
    ``names`` arguments.
    """
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, ''.join(list(names))))


def save_json_in_s3(json_data: dict, key: str, bucket=DEFAULT_S3_BUCKET):
    """
    Saves the given JSON data as bytes using the given key.
    """
    s3.put_object(
        Bucket=bucket,
        Key=key,
        # convert JSON dict to a byte string:
        Body=json.dumps(json_data).encode()
    )


def get_json_from_s3(key: str, bucket=DEFAULT_S3_BUCKET):
    """
    Returns the contents of the file as JSON whose key is specified.
    """
    response = s3.get_object(
        Bucket=bucket,
        Key=key
    )
    content = response['Body'].read()

    # get JSON as dict from a byte string
    return json.loads(content.decode())


def get_presigned_url(bucket_name, object_key, expiration=3600):
    """
    Generate a presigned URL to share an S3 object.

    :param bucket_name: string
    :param object_key: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """
    try:
        response = s3.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket_name,
                'Key': object_key,
            },
            ExpiresIn=expiration,
        )
    except ClientError as e:
        print(f'Error when generating a pre-signed URL: {e}')
        response = None

    return response
