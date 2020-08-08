import json

from boto3.dynamodb.conditions import Key

from utils.dynamodb import DynamoDbWrapper

dynamodb = DynamoDbWrapper()


class StatusCode:
    # 2xx:
    ok = 200
    created = 201
    # 4xx:
    bad_request = 400


class Asset:
    table_name = 'Assets'
    partition_key = 'type'
    sort_key = 'sk'
    asset_type = None   # used as the value of the partition key

    def _success_response(self, body={}, status_code=StatusCode.ok):
        return {
            'statusCode': status_code,
            'body': json.dumps(body),
        }

    def _error_response(self, body={}, status_code=StatusCode.bad_request):
        return {
            'statusCode': status_code,
            'body': json.dumps(body),
        }

    def list(self):
        """
        Get a list of assets from the asset's DynamoDB table.
        """
        assets = dynamodb.query(
            table_name=self.table_name,
            query=Key(self.partition_key).eq(self.asset_type),
        )
        # remove the partition key from the results:
        for asset in assets:
            asset.pop(self.partition_key)

        return self._success_response({
            'assets': assets,
        })


class IPAddress(Asset):
    asset_type = 'ip_address'


class Domain(Asset):
    asset_type = 'domain'


class ObjectStorage(Asset):
    asset_type = 'object_storage'


class DataStorage(Asset):
    asset_type = 'data_storage'


class APIEndpoint(Asset):
    asset_type = 'api_endpoint'


class CDN(Asset):
    asset_type = 'cdn'
