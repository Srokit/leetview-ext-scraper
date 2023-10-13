"""
Put the problem hint in a DynamoDB table where the key is the proble id

using boto3
"""

import boto3

def put_problem_hint_in_dyn_table(pid, hint):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('lv-prob-to-hint-table-v1')
    # Check success
    response = table.put_item(
         Item={
            'prob_id': pid,
            'hint': hint
        }
    )
    return response['ResponseMetadata']['HTTPStatusCode'] == 200

