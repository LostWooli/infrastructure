from __future__ import print_function
import json
import boto3
import logging
import pymysql
import socket
import re
import time

from botocore.exceptions import ClientError
from botocore.vendored import requests


logger = logging.getLogger()
logger.setLevel(logging.INFO)

def getusersecret(user, group):
    print("Getting User Secret")
    secret_name = f"/dbcreds/{user}"
    print(secret_name)
    client = boto3.client('secretsmanager')
    try:
        ############GET user secret dict#######
        print("Connection to secrets")
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        payload = get_secret_value_response.get('SecretString').encode('utf8')
        parsed = json.loads(payload)
        for key,values in parsed.items():
            host = key
            userpassword = values

            admin_password, admin_user = user_automation_admin_aws_credentials(host)

            initialize_database(host, admin_user, admin_password, user, userpassword, group)

    except ClientError as e:
        logging.error(e)
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            raise e


def user_automation_admin_aws_credentials(host):
    secret_name = "/dbcreds/app_admin"
    client = boto3.client('secretsmanager')

    print("Getting app_admin creds for " + host)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        payload = get_secret_value_response.get('SecretString').encode('utf8')
        parsed = json.loads(payload)

        for key,values in parsed.items():
            if key == host:
                return values, 'app_admin'

    except ClientError as e:
        logging.error(e)
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            raise e
            
def initialize_database(host, admin_user, admin_password, user, userpassword, group):
    try:
        if group != "application":
            user = f"{group}_{user}"
        print("initialize_database user " + user)
        testtcp(host)
        conn = pymysql.connect(host=host, user=admin_user, passwd=admin_password, connect_timeout=5)
        if group != "application":
            #user = f"{group}_{user}"
            print("Getting userlist from " + host)
            userlist = list_users(conn)
            if user in userlist:
                print(user + " is present")
                remove_users(conn, user)
            else:
                print(user + " is not present in the list")
        #execute_db(conn, user, userpassword, group)
    except (pymysql.MySQLError, pymysql.InternalError) as e:
        print('Got error {!r}, errno is {}'.format(e, e.args[0]))




##########Create DB User##############         
def execute_db(conn, user, userpassword, group):
    ###########PREFIX USERNAME##############
    with conn.cursor() as cur:
        cur.execute("SELECT VERSION()")
        version = cur.fetchone()
        #####EXECUTE DB QUEREY###############
        print("actual db username is " + user)
        cur.execute(f"call dba_tools.proc_create_user('{user}','%','{userpassword}','select','*.*');")

        
def testtcp(host):
    s = socket.socket()
    address = host
    port = 3306  # port number is a number, not string
    print("Testing connectivity for " + host)
    try:
        s.connect((address, port))
        print('Successful connection to ' + host)
    except: 
        print("Cannot connect to " + host)
    finally:
        s.close()
        
def list_users(conn):
    with conn.cursor() as cur:
        cur.execute(f"call dba_tools.proc_list_users();")
        tupuserlist = cur.fetchall()
        userlist = []
        for item in tupuserlist:
            userlist.append(item[0].split("'")[0])
        return(userlist)

def remove_users(conn, user):
    with conn.cursor() as cur:
        cur.execute(f"call dba_tools.proc_drop_user('{user}','%');")
        
def lambda_handler(event, context):
    for key,value in event.items():
        print(key)
        print(value)
        user = key
        group = value
        getusersecret(user, group)