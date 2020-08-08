import json

from utils.decorators import cors_headers
from utils.dynamodb import DynamoDbWrapper

from assets.core import (
    StatusCode,
    IPAddress,
    Domain,
    ObjectStorage,
    DataStorage,
    APIEndpoint,
    CDN,
)

dynamodb = DynamoDbWrapper()

asset_map = {
    'ip_address': IPAddress(),
    'domain': Domain(),
    'object_storage': ObjectStorage(),
    'data_storage': DataStorage(),
    'api_endpoint': APIEndpoint(),
    'cdn': CDN(),
}


@cors_headers
def list_assets(event, context):
    """
    Get a list of assets of the given type.

    Query string parameters
    -----------------------
    asset_type (required):
        The type of asset to get. Allowed values are found in the
        ``asset_map`` dict.
    """
    query_params = event.get('queryStringParameters', {})
    try:
        asset_type = query_params['asset_type']
    except KeyError:
        return {
            'statusCode': StatusCode.bad_request,
            'body': json.dumps({
                'error': 'Query string parameter `asset_type` is required'
            })
        }

    try:
        asset = asset_map[asset_type]
    except KeyError:
        return {
            'statusCode': StatusCode.bad_request,
            'body': json.dumps({
                'error': f'Invalid value for `asset_type`. '
                         f'Allowed values are {set(asset_map.keys())}'
            })
        }

    return asset.list()
