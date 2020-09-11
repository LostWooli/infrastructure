from __future__ import print_function
from botocore.vendored import requests
import json
import logging
import os
import boto3
import socket
import http.client as httplib

def ssm_aws_parameter():
    ssm = boto3.client('ssm')
    response = ssm.get_parameter(
    Name='/devops/main-dev-endpoints',
    WithDecryption=True
    )
    response_parsed = json.loads(response.get('Parameter').get('Value'))
    return response_parsed
    
    
def lambda_handler(event, context):
    response_parsed = ssm_aws_parameter()
    for url, path in response_parsed.items():
        conn = httplib.HTTPSConnection(url)
        conn.request("GET", path)
        res = conn.getresponse()
        date = (res.getheader("Date"))

        json_response = {
            "date": date,
            "endpoint": url + path,
            "status": res.status,
            "reason": res.reason
        }
        message = json_response
        print(message)
        
        bytes_message = json.dumps(message)
        host = os.environ['splunkurl']
        port = 9999
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.sendall(bytes_message.encode('utf-8'))
        
    