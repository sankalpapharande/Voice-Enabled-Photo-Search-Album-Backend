from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3
import json
import re

host = 'search-photos-2-7rskrx3yn5dfcxg3oekayi2eei.us-east-1.es.amazonaws.com'
region = 'us-east-1'
service = 'es'
headers = {"Content-Type": "application/json"}
credentials = boto3.Session().get_credentials()
#awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
awsauth = ('open-search-user', 'User@1234')
open_search_client = OpenSearch(
        hosts = [{'host': host, 'port': 443}],
        http_auth = awsauth,
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
        )


def get_images_from_keywords(keywords):
    query_results = []
    for label in keywords:
        search_query_output = open_search_client.search(index="photos", body={"query":{"match":{"labels":label}}})
        query_results.append(search_query_output)
    return query_results

def get_image_names(open_search_results):
    name_labels_dict = {}
    for result in open_search_results:
        for hit in result['hits']['hits']:
            image_name = hit['_source']['objectKey']
            labels = hit['_source']['labels']
            if image_name not in name_labels_dict.keys():
                name_labels_dict[image_name] = labels
    return name_labels_dict


SINGULAR_SUFFIX = [
    ('people', 'person'),
    ('men', 'man'),
    ('wives', 'wife'),
    ('menus', 'menu'),
    ('us', 'us'),
    ('ss', 'ss'),
    ('is', 'is'),
    ("'s", "'s"),
    ('ies', 'y'),
    ('ies', 'y'),
    ('es', 'e'),
    ('s', '')
]

def singularize(noun):
    for suffix, singular_suffix in SINGULAR_SUFFIX:
        if noun.endswith(suffix):
            return noun[:-len(suffix)] + singular_suffix
    return noun

def get_open_search_supported_keywords(keywords):
    modified_keywords = []
    for keyword in keywords:
        if keyword is not None:
            modified_keywords.append(singularize(keyword).capitalize())
    return modified_keywords
    
def lambda_handler(event, context):
    try:
        print("event:{}".format(event))
        print("context:{}".format(context))
        # Lex will give keywords
        print("creating lex client")
        lex_bot_client = boto3.client('lexv2-runtime')
        print("lex client created")
        print(lex_bot_client)
        
        #user_input = "get me pics of dogs and cats"
        # user_input = "Show me pics of dogs and cats"
    
        
        user_input = event["queryStringParameters"]["q"]
        #user_input = "get me pics of Cat"
        
        print("User Input:{}".format(user_input))
        
        
        
        response = lex_bot_client.recognize_text(
                botAliasId="TSTALIASID",
                botId="1RBXMHAUMG",
                localeId= "en_US",
                text = user_input,
                sessionId= "877755470769942"
            )
        
        print("*******************Lex bot response:{}".format(response))
        
        keywords = []
        q1_value = response["sessionState"]["intent"]["slots"]["q1"]
        q2_value = response["sessionState"]["intent"]["slots"]["q2"]
        print(response["sessionState"]["intent"]["slots"])
        if q1_value is not None:
            keywords.append(q1_value["value"]["interpretedValue"])
        
        if q2_value is not None:
            keywords.append(q2_value["value"]["interpretedValue"])
        
        
        modified_keywords = get_open_search_supported_keywords(keywords)
        
        print("Keywords are:{}".format(keywords))
        print("Modified keywords are:{}".format(modified_keywords))
        open_search_results = get_images_from_keywords(modified_keywords)
        print(open_search_results)
        
        image_names_labels = get_image_names(open_search_results)
        base_url = "https://yuktib2.s3.amazonaws.com/"
        results = []
        for image in image_names_labels.keys():
            image_info_json = {}
            image_info_json["url"] = base_url+image
            image_info_json["labels"] = image_names_labels[image]
            results.append(image_info_json)
        
        print("The result images are:{}".format(results))
        return {
        'statusCode': 200,
        'headers':{
            'Access-Control-Allow-Origin':'*',
            'Access-Control-Allow-Credentials':True
            # 'Access-Control-Request-Headers':'*',
            # 'Access-Control-Allow-Headers':'*'
        },
        'body': json.dumps({"results":results})
    }
        
    except Exception as e:
        return {
            'code': 0,
            'message': str(e)
        }
