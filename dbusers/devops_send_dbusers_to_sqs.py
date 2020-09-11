from __future__ import print_function
import json
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def list_users() -> list:
        client = boto3.client('iam')
        response = client.list_users(
            MaxItems=1000
        )
        return [item.get('UserName') for item in response.get('Users')]
def listusertags():
    user_list_for_access = []
    userlist = list_users()
    client = boto3.client('iam')
    for item in userlist:
        response = client.get_user(
                UserName=item
        )
        try:
            
            tags = response.get('User')['Tags']
            #print(tags)
            user_name = response.get('User').get('UserName')
            #print(user_name)
            dbaccess = ''
            for tag_item in tags:
                if tag_item['Key'].lower() == 'dbaccess' and tag_item['Value'].lower() == 'developer':
                    #print(tag_item)
                    dbaccess = tag_item.get('Value').lower()
                    user_list_for_access.append({user_name: dbaccess})
                    #print(user_list_for_access)

                if tag_item['Key'].lower() == 'dbaccess' and tag_item['Value'].lower() == 'application':
                    dbaccess = tag_item.get('Value').lower()
                    user_list_for_access.append({user_name: dbaccess})

        except KeyError:
            pass
    return user_list_for_access
# def sendtosqs():
#     client = boto3.client('sqs')
#     for user in listusertags():
#         # test
#         print(user)
#         for keys, values in user.items():
#             response = client.send_message(
#                 QueueUrl='https://sqs.us-east-1.amazonaws.com/492239587024/devopsgetdbusersprd',
#                 MessageBody=keys
#                 )

def sendtosqs():
    client = boto3.client('sqs')
    for user in listusertags():
        # test
        user_string = json.dumps(user)
        print(user_string)
        response = client.send_message(
                QueueUrl='https://sqs.us-east-1.amazonaws.com/492239587024/devopsgetdbusersprd',
                MessageBody=user_string
                )

def lambda_handler(event, context):
    print(sendtosqs())
