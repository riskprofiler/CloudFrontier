import decimal
import json
import os

from utils.dynamodb import DynamoDbWrapper
from utils.utils import get_json_from_s3

dynamodb = DynamoDbWrapper()

table_name = os.environ['DynamoDBTableAssets']


def handler(event, context):
    message_json = json.loads(event['Records'][0]['Sns']['Message'])
    print(message_json)
    asset_type = message_json['type']
    domain_or_ip = message_json['domain_or_ip']
    s3_key = message_json['s3_key']

    collected_data = get_json_from_s3(s3_key)

    ports = collected_data.get('ports')
    country_name = collected_data.get('country_name')
    asn = collected_data.get('asn')
    country_code = collected_data.get('country_code')
    vulns = collected_data.get('vulns')
    latitude = collected_data.get('latitude')
    if latitude:
        latitude = decimal.Decimal(str(latitude))
    longitude = collected_data.get('longitude')
    if longitude:
        longitude = decimal.Decimal(str(longitude))

    dynamodb.update_item(
        table_name=table_name,
        primary_key={
            'type': asset_type,
            'sk': domain_or_ip
        },
        update={
            'ports': ports,
            'country_code': country_code,
            'asn': asn,
            'country_name': country_name,
            'vulns': vulns,
            'latitude': latitude,
            'longitude': longitude,
        },
    )
