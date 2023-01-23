import boto3
from botocore.exceptions import ClientError
aws_region = 'us=east-1'
athena_client = boto3.client("athena")

def lambda_handler(event, context):
    query_result_bucket = 's3://temp-bucket-umair/results/'
    if('source' in event):
        query_result_bucket = 's3://temp-bucket-umair/scheduled/'
    database = 'employee'
    response = ''
    print(event)
    query = event["query"]
    response = ''
    try:
        response = athena_client.start_query_execution(
            QueryString=query,
            QueryExecutionContext={
                'Database': database,
            },
            ResultConfiguration={
                'OutputLocation': query_result_bucket,
            },
            WorkGroup='my-workgroup'
        )
    except ClientError as e:
        response = e.response['Error']['Message']
    
    return response