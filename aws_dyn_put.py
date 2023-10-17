"""
Put the problem hint in a DynamoDB table where the key is the proble id

using boto3
"""

import boto3

# Change when using a diff model
CURR_MODEL = "gpt-3.5-turbo"
# CURR_MODEL = "gpt-4"

def put_problem_hint_in_dyn_table(pid, hint):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('lv-prob-to-hint-table-v1')
    # Check success
    response = table.put_item(
         Item={
            'prob_id': pid,
            'hint': hint,
            'model': CURR_MODEL,
        }
    )
    return response['ResponseMetadata']['HTTPStatusCode'] == 200


def check_if_problem_in_dyn_table(pid):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('lv-prob-to-hint-table-v1')
    response = table.get_item(
        Key={
            'prob_id': pid
        }
    )
    return 'Item' in response

