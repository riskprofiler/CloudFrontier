import os

import boto3

dynamodb = boto3.resource('dynamodb')
counts_table = dynamodb.Table(os.environ['DynamoDBTableCounts'])

administrative_ports = {
    20,     # FTP
    21,     # FTP
    22,     # SSH
    23,     # Telnet
    25,     # SMTP
    53,     # DNS
    67,     # DHCP
    68,     # DHCP
    110,    # POP3
    143,    # IMAP
    161,    # SNMP
    993,    # IMAP
    3389,   # RDP
}


def get_new_keys(old_image: dict, new_image: dict):
    """
    Returns the keys that were no added in the new image.
    """
    old_keys = set(old_image.keys())
    new_keys = set(new_image.keys())
    return new_keys - old_keys


def update_for_ports(new_image, updates):
    ports = [int(i['N']) for i in new_image['ports']['L']]
    # update the total count of open ports:
    category = 'summary'
    value = 'open_ports'
    additional_count = len(ports)
    updates.append((category, value, additional_count))
    # update the count of each port based on its category (commmon
    # or administrative):
    for port in ports:
        if port in administrative_ports:
            category = 'admin_port'
        else:
            category = 'common_port'
        value = port
        additional_count = 1
        updates.append((category, value, additional_count))


def update_for_vulns(new_image, updates):
    if new_image['vulns'].get('NULL') is not True:
        vulns = [i['S'] for i in new_image['vulns']['L']]
        # update the total count of vulnerabilities:
        category = 'summary'
        value = 'vulns'
        additional_count = len(vulns)
        updates.append((category, value, additional_count))
        # update the count of each vulnerability (CVE):
        for cve in vulns:
            category = 'vuln'
            value = cve
            additional_count = 1
            updates.append((category, value, additional_count))


def process_stream_record(record):
    """
    Identifies which counts need to be updated for a given stream record.
    """
    new_image = record['dynamodb']['NewImage']
    event_name = record['eventName']
    updates = []
    if event_name == 'INSERT':
        # A new asset has been collected. Increment the count of its type by 1:
        asset_type = new_image['type']['S']
        value = asset_type
        category = 'asset'
        additional_count = 1
        updates.append((category, value, additional_count))
    elif event_name == 'MODIFY':
        old_image = record['dynamodb']['OldImage']
        # Check which attribute was added by some analyzer:
        new_keys = get_new_keys(old_image, new_image)
        for key in new_keys:
            if key == 'ports':
                update_for_ports(new_image, updates)
            elif key == 'vulns':
                update_for_vulns(new_image, updates)

    return updates


def handler(event, context):
    # The keys in the `updates` dict are a combination of the `category` and
    # `value` whose count is to be updated, and the value is the count to be
    # added in DynamoDB.
    updates = {}
    for record in event['Records']:
        if record['eventName'] not in ['INSERT', 'MODIFY']:
            continue    # we only need to process the new and modified items
        record_updates = process_stream_record(record)
        for category, value, additional_count in record_updates:
            category_and_value = f'{category}:{value}'
            if updates.get(category_and_value) is None:
                # set the initial value to 0 if the key didn't already exist
                updates[category_and_value] = 0
            updates[category_and_value] += additional_count

    for category_and_value, additional_count in updates.items():
        category, value = category_and_value.split(':', 1)
        counts_table.update_item(
            Key={
                'category': category,
                'value': value,
            },
            UpdateExpression=f'ADD #c :a',
            ExpressionAttributeNames={
                '#c': 'count',
            },
            ExpressionAttributeValues={
                ':a': additional_count,
            },
        )
