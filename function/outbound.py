# This function is triggered via API Gateway when a user acts on the Slack interactive message sent by approval_requester.py.

from urllib.parse import parse_qs
import json
import os
import boto3
from botocore.exceptions import ClientError

SLACK_VERIFICATION_TOKEN = os.environ['SLACK_VERIFICATION_TOKEN']

#Triggered by API Gateway
#It kicks off a particular CodePipeline project
def lambda_handler(event, context):
  print("Received event: " + json.dumps(event, indent=2))
  body = parse_qs(event['body'])
  payload = json.loads(body['payload'][0])

  approver_username = (payload['user']['name'])
  action_details = json.loads(payload['actions'][0]['value'])
  statusBool = action_details["approve"]
  codepipeline_name = action_details["codePipelineName"]
  codepipeline_token = action_details["codePipelineToken"]
  stageName = action_details["codePipelineStage"] 
  actionName = action_details["codePipelineAction"]
  codepipeline_status = "Approved" if statusBool else "Rejected"

  # Validate Slack token
  if SLACK_VERIFICATION_TOKEN == payload['token']:
    result = send_slack_message(codepipeline_name, codepipeline_token, codepipeline_status, stageName, actionName)
    # This will replace the interactive message with a simple text response.
    # You can implement a more complex message update if you would like.
    if result:
      return  {
        "isBase64Encoded": "false",
        "statusCode": 200,
        "body": "{\"text\": \"Approval of stage: " + stageName + " requested by " + approver_username + " has been " + codepipeline_status + "\"}"
      }
    else:
      return  {
        "isBase64Encoded": "false",
        "statusCode": 200,
        "body": "{\"text\": \"Approval of stage: " + stageName + " requested by " + approver_username + " has failed. \"}"
      }
  else:
    return  {
      "isBase64Encoded": "false",
      "statusCode": 403,
      "body": "{\"error\": \"This request does not include a vailid verification token.\"}"
    }

def send_slack_message(name, token, status, stageName, actionName):
  try:
    client = boto3.client('codepipeline')
    response_approval = client.put_approval_result(
              pipelineName=name,
              stageName=stageName,
              actionName=actionName,
              result={'summary':'','status':status},
              token=token)
    print(response_approval)
    return True
  except ClientError as e:
    print(e)
    return False