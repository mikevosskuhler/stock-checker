import json
import boto3
import json
from boto3.dynamodb.types import TypeDeserializer


def lambda_handler(event, context):
    
    client = boto3.client('dynamodb')
    scan=client.scan(TableName='webcrawler_products')
    products = scan['Items']
    
    deser = TypeDeserializer()
    
    sqs_client = boto3.client('sqs')
    
    entries = []
    i = 0
    for product in products:
         entries.append({'Id': str(i), 'MessageBody': 
                          json.dumps({'url': deser.deserialize(product['url']), 
                          'product': deser.deserialize(product['product']),
                          'category': deser.deserialize(product['category'])})})
         i += 1
    
    i = 0
    while i < len(entries):
         response = sqs_client.send_message_batch(
                   QueueUrl='https://sqs.eu-central-1.amazonaws.com/022998352254/testqueue2',
                   Entries=entries[i:i+10])
         i += 10


    return {
        'statusCode': 200,
        'body': json.dumps('success!')
    }
