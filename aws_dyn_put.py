"""
Put the problem hint in a DynamoDB table where the key is the proble id

using boto3
"""

import boto3

from scrape_config import MODEL

def put_problem_hint_in_dyn_table(pid, hint):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('lv-prob-to-hint-table-v1')
    # Check success
    response = table.put_item(
         Item={
            'prob_id': pid,
            'hint': hint,
            'model': MODEL,
        }
    )
    return response['ResponseMetadata']['HTTPStatusCode'] == 200

def get_all_pids_in_dyn_table():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('lv-prob-to-hint-table-v1')
    # items = set(i['prob_id'] for i in response['Items'])

    # Handle multiple pages of results
    items = set()
    response = table.scan()
    items.update(i['prob_id'] for i in response['Items'])
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.update(i['prob_id'] for i in response['Items'])
    return items

