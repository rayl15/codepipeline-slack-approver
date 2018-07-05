# This function is invoked via SNS when the CodePipeline manual approval action starts.
# It will take the details from this approval notification and sent an interactive message to Slack that allows users to approve or cancel the deployment.

import os
import json
import logging
import urllib.parse

from base64 import b64decode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# This is passed as a plain-text environment variable for ease of demonstration.
# Consider encrypting the value with KMS or use an encrypted parameter in Parameter Store for production deployments.
SLACK_WEBHOOK_URL = os.environ['SLACK_WEBHOOK_URL']
SLACK_CHANNEL = os.environ['SLACK_CHANNEL']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    message = event["Records"][0]["Sns"]["Message"]
    
    data = json.loads(message) 
    token = data["approval"]["token"]
    codepipeline_region = data["region"]
    codepipeline_console_link = data["consoleLink"]
    codepipeline_name = data["approval"]["pipelineName"]
    codepipeline_stage_name = data["approval"]["stageName"]
    codepipeline_action_name = data["approval"]["actionName"]
    codepipeline_action_expiry = data["approval"]["expires"]
    codepipeline_approval_review = data["approval"]["approvalReviewLink"]
    codepipeline_approval_custom_data = data["approval"]["customData"]
    
    slack_message = {
        "channel": SLACK_CHANNEL,
        "text": "<!here|here> Approval required for " + codepipeline_name + " at " + codepipeline_stage_name + "/" + codepipeline_action_name + ". Expires at " + codepipeline_action_expiry,
        "attachments": [
            {
                "pretext": "Approval required!",
                "title": "CodePipeline Console Link",
                "title_link": codepipeline_console_link,
                "text": "Yes to approve and continue this stage:" + codepipeline_stage_name,
                "fallback": "Error, You are unable to approve pipelines",
                "callback_id": "codepipeline",
                "color": "#3AA3E3",
                "attachment_type": "default",
                "fields": [
                    {
                        "title": "CodePipeline Stage Name",
                        "value": codepipeline_stage_name,
                        "short": "true"
                    },
                    {
                        "title": "CodePipeline Action Name",
                        "value": codepipeline_action_name,
                        "short": "true"
                    },
                    {
                        "title": "CodePipeline Approval Expires",
                        "value": codepipeline_action_expiry,
                        "short": "true"
                    }

                ],
                "actions": [
                    {
                        "name": "deployment",
                        "text": "Approve",
                        "style": "danger",
                        "type": "button",
                        "value": json.dumps({"approve": True, "codePipelineToken": token, "codePipelineName": codepipeline_name, "codePipelineStage": codepipeline_stage_name, "codePipelineAction": codepipeline_action_name}),
                        "confirm": {
                            "title": "Are you sure?",
                            "text": "This will approve and continue this stage:" + codepipeline_stage_name,
                            "ok_text": "Yes",
                            "dismiss_text": "No"
                        }
                    },
                    {
                        "name": "deployment",
                        "text": "No",
                        "type": "button",
                        "value": json.dumps({"approve": False, "codePipelineToken": token, "codePipelineName": codepipeline_name, "codePipelineStage": codepipeline_stage_name, "codePipelineAction": codepipeline_action_name})
                    }  
                ]
            }
        ]
    }

    req = Request(SLACK_WEBHOOK_URL, json.dumps(slack_message).encode('utf-8'))

    response = urlopen(req)
    response.read()
    
    return None