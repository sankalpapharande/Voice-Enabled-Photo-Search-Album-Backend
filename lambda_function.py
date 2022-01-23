from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3
import json
import time
from botocore.vendored import requests

#host = 'vpc-photos-jggnnh7gdds7imimmgdtgtty7q.us-east-1.es.amazonaws.com' # For example, my-test-domain.us-east-1.es.amazonaws.com
#host = 'search-photos2-tdwob5ezexmq2xdpkd2otj4fnm.us-east-1.es.amazonaws.com'
host = 'search-photos-2-7rskrx3yn5dfcxg3oekayi2eei.us-east-1.es.amazonaws.com'
region = 'us-east-1'
service = 'es'
headers = {"Content-Type": "application/json"}
credentials = boto3.Session().get_credentials()
#awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
aws_auth = ('open-search-user', 'User@1234')
open_search_client = OpenSearch(
        hosts = [{'host': host, 'port': 443}],
        http_auth = aws_auth,
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
        )

aws_rekognition_client = boto3.client('rekognition')

def lambda_handler(event, context):
    print("ADDED A PRINT LINE FOR CODEPIPELINE TESTING-1")
    print("Event is:{}".format(event))
    print("testing deployment pipeline")
    count = 0
    print("Opensearch Connection Object Info:{}".format(open_search_client))
    for record in event['Records']:
        key = record['s3']['object']['key']
        name = record['s3']['bucket']['name']
        
        print("Key:{}".format(key))
        print("name:{}".format(name))
        
        aws_rekognition_response = aws_rekognition_client.detect_labels(Image={'S3Object': {'Bucket': name, 'Name': key}},
            MaxLabels=10, 
            MinConfidence=80)
            
        print("Rekognition Response: {}".format(aws_rekognition_response))
        
        timestamp =time.time()
        
        labels = []
        for label in aws_rekognition_response['Labels']:
            labels.append(label['Name'])
        print(labels)
        required_json_format = {'objectKey':key,'bucket':name,'createdTimestamp':timestamp,'labels':labels}
        print("JSON to open search:{}".format(required_json_format))
        open_search_client.index(index="photos", 
            doc_type="Photo", 
            id=key, 
            body=json.dumps(required_json_format).encode("utf-8"), 
            refresh=True)

        count = count + 1
    print("Successfully uploaded:{}".format(count))
    return {
        'statusCode': 200,
        'headers':{
            'Access-Control-Allow-Origin':'*',
            'Access-Control-Allow-Credentials':True,
            'Access-Control-Request-Headers':'*',
            'Access-Control-Allow-Headers':'*'
            
        },
        'body': json.dumps({"no_of_recrods_inserted":count})
    }
