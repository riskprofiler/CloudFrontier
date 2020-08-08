import datetime
import decimal
import json

import boto3


class DynamoDbWrapper:
    """
    Wrapper class for DynamoDB.
    """
    def __init__(self):
        self.resource = boto3.resource('dynamodb')

    class DoesNotExist(Exception):
        """
        Raised when an item whose primary key is given does not exist in
        DynamoDB.
        """
        pass

    def batch_writer(self, table_name: str, data_list: list):
        """
        :param table_name: Name of the DynamoDB table to save the data in.
        :param data_list: List of data to bulk save.
        """
        table = self.resource.Table(table_name)
        with table.batch_writer() as batch:
            for data in data_list:
                batch.put_item(
                    Item=json.loads(
                        json.dumps(
                            data,
                            cls=DynamoDBEncoder,
                        ),
                        parse_float=decimal.Decimal,
                    )
                )
        print(f'Saved {len(data_list)} items in DynamoDB table {table_name}')

    def insert(self, table_name: str, item: dict):
        """
        Insert or overwrite an item in the given DynamoDB table.

        Arguments
        ---------
        table_name : str
            The name of the DynamoDB table in which the item is to be inserted.
        item : dict
            The item that is to be inserted or overwritten in the table. This
            must contain at least those attributes that make up the primary
            key. If an item with the primary key already exists, it will be
            overwritten with this item.
        """
        table = self.resource.Table(table_name)
        table.put_item(
            Item=json.loads(
                json.dumps(
                    item,
                    cls=DynamoDBEncoder,
                ),
                parse_float=decimal.Decimal,
            )
        )
        print(f'Inserted item in DynamoDB table {table_name}')

    def get_item(self, table_name: str, primary_key: dict) -> dict:
        """
        Get an item from the given DynamoDB table that matches the given
        `primary_key`.

        Arguments
        ---------
        table_name : str
            The name of the DynamoDB table to get the item from.
        primary_key : dict
            A dictionary that describes the primary key of the item to get.
            This should have the partition key and optionally the sort key if
            the table has a composite primary key.
        """
        table = self.resource.Table(table_name)
        response = table.get_item(Key=primary_key)
        try:
            return json.loads(json.dumps(response['Item'], cls=DynamoDBEncoder))
        except KeyError:
            raise DynamoDbWrapper.DoesNotExist(
                'No item matching the primary key was found.'
            )

    def delete_item(self, table_name: str, primary_key: dict):
        """
        Delete an item from the given DynamoDB table that matches the given
        `primary_key`.

        Arguments
        ---------
        table_name : str
            The name of the DynamoDB table from where to delete the item.
        primary_key : dict
            A dictionary that describes the primary key of the item to delete.
            This should have the partition key and optionally the sort key if
            the table has a composite primary key.
        """
        table = self.resource.Table(table_name)
        table.delete_item(Key=primary_key)

    def scan(self, table_name: str, condition: str = None,
             projection_expression: str = None) -> list:
        """
        Uses the scan method of DynamoDB and returns all the items in the
        given table that match the given optional ``condition``.

        Optional arguments
        ------------------
        condition : str
            The condition to filter the items.
        projection_expression : str
            Comma-separated list of field names that are the only ones to be
            included in the output. If it's empty then all of the fields are
            included.
        """
        table = self.resource.Table(table_name)

        scan_kwargs = {}
        if condition:
            scan_kwargs['FilterExpression'] = condition
        if projection_expression:
            scan_kwargs['ProjectionExpression'] = projection_expression
        response = table.scan(**scan_kwargs)

        items = []
        for item in response['Items']:
            items.append(json.loads(json.dumps(item, cls=DynamoDBEncoder)))

        while response.get('LastEvaluatedKey') is not None:
            last_evaluated_key = response['LastEvaluatedKey']
            scan_kwargs['ExclusiveStartKey'] = last_evaluated_key
            response = table.scan(**scan_kwargs)
            for item in response['Items']:
                items.append(json.loads(json.dumps(item, cls=DynamoDBEncoder)))

        return items

    def query(self, table_name: str, query: str, filter_expression: str = None,
              projection_expression: str = None) -> list:
        """
        Uses the query method of DynamoDB and returns all the items in the
        given table that match the given ``query`` optional
        ``filter_expression`` conditions.

        Arguments
        ---------
        table_name : str
            Name of the table in which the item is to be updated.
        query : str
            The condition to query the items. This must contain the table's
            partition key and optionally the sort key.

        Optional arguments
        ------------------
        filter_expression : str
            The condition to filter the items after they have been queried.
        projection_expression : str
            Comma-separated list of field names that are the only ones to be
            included in the output. If it's empty then all of the fields are
            included.
        """
        table = self.resource.Table(table_name)

        query_kwargs = {
            'KeyConditionExpression': query,
        }
        if filter_expression:
            query_kwargs['FilterExpression'] = filter_expression
        if projection_expression:
            query_kwargs['ProjectionExpression'] = projection_expression
        response = table.query(**query_kwargs)

        items = []
        for item in response['Items']:
            items.append(json.loads(json.dumps(item, cls=DynamoDBEncoder)))

        while response.get('LastEvaluatedKey') is not None:
            last_evaluated_key = response['LastEvaluatedKey']
            query_kwargs['ExclusiveStartKey'] = last_evaluated_key
            response = table.query(**query_kwargs)
            for item in response['Items']:
                items.append(json.loads(json.dumps(item, cls=DynamoDBEncoder)))

        return items

    def query_page(self, table_name: str, query: str,
                   filter_expression: str = None,
                   projection_expression: str = None,
                   limit: int = 25,
                   exclusive_start_key: dict = None):
        """
        Uses the query method of DynamoDB and returns up to the given ``limit``
        of items in the given table that match the given ``query`` and optional
        ``filter_expression`` conditions. If the ``exclusive_start_key`` is
        also given, then items after that key will be queried.

        Arguments
        ---------
        table_name : str
            Name of the table in which the item is to be updated.
        query : str
            The condition to query the items. This must contain the table's
            partition key and optionally the sort key.

        Optional arguments
        ------------------
        filter_expression : str
            The condition to filter the items after they have been queried.
        projection_expression : str
            Comma-separated list of field names that are the only ones to be
            included in the output. If it's empty then all of the fields are
            included.
        limit : int (default=25)
            The maximum number of items to query.
        exclusive_start_key : dict
            The primary of the item after which the results are to be queried.
        """
        table = self.resource.Table(table_name)

        query_kwargs = {
            'KeyConditionExpression': query,
        }
        if filter_expression:
            query_kwargs['FilterExpression'] = filter_expression
        if projection_expression:
            query_kwargs['ProjectionExpression'] = projection_expression
        if exclusive_start_key:
            query_kwargs['ExclusiveStartKey'] = exclusive_start_key
        if limit:
            query_kwargs['Limit'] = limit
        response = table.query(**query_kwargs)

        items = []
        for item in response['Items']:
            items.append(json.loads(json.dumps(item, cls=DynamoDBEncoder)))

        last_evaluated_key = response.get('LastEvaluatedKey')

        return items, last_evaluated_key

    def count(self, table_name: str, query: str,
              filter_expression: str = None) -> int:
        """
        Returns the count of all the items in the given table that match the
        given ``query`` and the optional ``filter_expression``.

        Arguments
        ---------
        table_name : str
            Name of the table in which the item is to be updated.
        query : str
            The condition to query the items. This must contain the table's
            partition key and optionally the sort key.

        Optional arguments
        ------------------
        filter_expression : str
            The condition to filter the items.
        """
        table = self.resource.Table(table_name)

        query_kwargs = {
            'KeyConditionExpression': query,
        }
        if filter_expression:
            query_kwargs['FilterExpression'] = filter_expression

        response = table.query(**query_kwargs)
        count = response['Count']

        while response.get('LastEvaluatedKey') is not None:
            last_evaluated_key = response['LastEvaluatedKey']
            query_kwargs['ExclusiveStartKey'] = last_evaluated_key
            response = table.query(**query_kwargs)
            count += response['Count']

        return count

    def update_item(self, table_name: str, primary_key: dict, update: dict):
        """
        Update the item matching the primary key in the given table with the
        new key values from the ``update`` dictionary.

        Arguments
        ---------
        table_name : str
            Name of the table in which the item is to be updated.
        primary_key : dict
            A dictionary that describes the primary key of the item to update.
            This should have the partition key and optionally the sort key if
            the table has a composite primary key.
        update : dict
            A dictionary containing the keys and their values that are to be
            updated .

        Example
        -------
        ```
        update_item(
            table_name='users',
            primary_key={
                'organization_id': organization_id,
                'user_id': user_id,
            },
            update={
                'name': name,
                'address': {
                    'city': city,
                    'zip': zip_code,
                }
            })
        ```
        """
        table = self.resource.Table(table_name)

        update_expression = 'SET '
        updates = []
        for key, value in update.items():
            # Add a suffix the key to create a substitute name for it to
            # prevent conflicts with a reserved DynamoDB word.
            # Refer the following for more details:
            # - https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_UpdateItem.html
            # - https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/ReservedWords.html
            substitute_key = f'#{key}_key'
            substitute_value = f':{key}_value'
            updates.append({
                'key': key,
                'value': value,
                'substitute_key': substitute_key,
                'substitute_value': substitute_value,
            })
            update_expression += f'{substitute_key} = {substitute_value}, '
        update_expression = update_expression[:-2]  # remove the last ', '

        table.update_item(
            Key=primary_key,
            UpdateExpression=update_expression,
            ExpressionAttributeNames={
                u['substitute_key']: u['key'] for u in updates
            },
            ExpressionAttributeValues={
                u['substitute_value']: u['value'] for u in updates
            },
        )

    def increment_attributes(self, table_name: str, primary_key: dict, attributes: dict):
        """
        Adds the given value to the attributes' key in the item matching the
        given primary key.

        Arguments
        ---------
        table_name : str
            Name of the table in which the item is to be updated.
        primary_key : dict
            A dictionary that describes the primary key of the item to update.
            This should have the partition key and optionally the sort key if
            the table has a composite primary key.
        attribute : dict
            A dictionary containing the key and increment value of the
            attributes that are to be incremented.
        """
        table = self.resource.Table(table_name)
        for key, value in attributes.items():
            table.update_item(
                Key=primary_key,
                UpdateExpression=f'ADD #k :v',
                ExpressionAttributeNames={
                    '#k': key,
                },
                ExpressionAttributeValues={
                    ':v': decimal.Decimal(str(float(value))),   # this takes care of all edge cases
                },
            )


class DynamoDBEncoder(json.JSONEncoder):
    """
    Converts Python objects into the appropriate DynamoDB types.
    """
    def default(self, obj):
        # convert Decimal objects to float or int (depending on the value)
        if isinstance(obj, decimal.Decimal):
            if abs(obj) % 1 > 0:
                return float(obj)
            else:
                return int(obj)

        # convert datetime objects to string
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()

        return super(DynamoDBEncoder, self).default(obj)