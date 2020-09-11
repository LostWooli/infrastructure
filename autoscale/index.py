from __future__ import print_function
import base64
import string
import http.client as httplib
import boto3
import datetime
import json
import time
import os
import re

def connectivity_test():
    print("----checking connectivity to jenkins-------")
    conn = httplib.HTTPConnection('3.215.242.186:8000')
    conn.request("HEAD","/login?from=%2F")
    res = conn.getresponse()
    print(res.status)
    print(res.reason)
    conn.close()
    print("----checking connectivity end-------")

def trigger_jenkins_job(application, environment):
    print("----trigger jenkins job start-------")
    print("executing ")
    JOB_NAME = application+"/job/"+environment
    print(JOB_NAME)
    conn = httplib.HTTPConnection('3.215.242.186:8000')
    auth = (os.environ.get("auth"))
    head = { 'Authorization' : 'Basic %s' %  auth }
    conn.request("POST", "/job/"+(JOB_NAME)+"/build", headers = head)
    res = conn.getresponse()
    print(res.status)
    print(res.reason)
    conn.close()
    print("----trigger jenkins job end-------")


def lambda_handler(event, context):
    for record in event['Records']:
       message_json = json.loads(record["body"])["Message"]
       print(message_json)
       message = json.loads(message_json)
       print(message)
       group_arn = message["AutoScalingGroupARN"]
       print(group_arn)
       jobname = re.search(".*?autoScalingGroupName/(.*)-(.*)-(.*)", group_arn)
       print(jobname)
       
       application = (jobname.group(1))
       environment = (jobname.group(2))


    connectivity_test()
    trigger_jenkins_job(application, environment)