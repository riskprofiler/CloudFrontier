import os

import boto3
from botocore.exceptions import ClientError

from common import AWSServiceCollector

sts = boto3.client('sts')


class S3Collector(AWSServiceCollector):
    boto3_service_name = 's3'

    def _collect_assets(self):
        response = self.client.list_buckets()
        buckets = response['Buckets']
        # TODO: run each iteration asynchronously:
        for bucket in buckets:
            bucket_name = bucket['Name']
            # get the bucket's region:
            response = self.client.get_bucket_location(Bucket=bucket_name)
            region = response['LocationConstraint']
            if region is None:
                region = 'us-east-1'
                bucket_domain = f'{bucket_name}.s3.amazonaws.com'
            else:
                bucket_domain = f'{bucket_name}.s3.{region}.amazonaws.com'
            self.object_storage_endpoints.add(bucket_domain)

            # get ACL to check for public access:
            public_group_uris = [
                'http://acs.amazonaws.com/groups/global/AllUsers',
                'http://acs.amazonaws.com/groups/global/AuthenticatedUsers',
            ]
            public_permissions = ['FULL_CONTROL', 'WRITE', 'WRITE_ACP', 'READ']
            response = self.client.get_bucket_acl(Bucket=bucket_name)
            grants = response.get('Grants', [])
            is_public = False
            for grant in grants:
                permission = grant['Permission']
                grantee = grant['Grantee']
                grantee_uri = grantee.get('URI')
                if grantee_uri in public_group_uris and permission in public_permissions:
                    is_public = True
            self.object_storage_endpoint_attributes[bucket_domain] = {
                'is_public': is_public,
            }

            # get the bucket website:
            try:
                response = self.client.get_bucket_website(Bucket=bucket_name)
                bucket_website_domain = \
                    f'{bucket_name}.s3-website-{region}.amazonaws.com'
                self.domains.add(bucket_website_domain)
            except ClientError:
                pass    # website not available


def handler_global(event, context):
    response = sts.assume_role(
        RoleArn=os.environ['AWSIAMRoleARN'],
        RoleSessionName='CloudFrontierAssetCollector',
        # ExternalId='...',
    )
    print(f'Assumed IAM role')

    credentials = response['Credentials']
    client_session = boto3.Session(
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken'],
    )
    print(f'Created session')

    S3Collector(client_session).collect()
