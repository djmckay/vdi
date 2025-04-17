import json
import os
def lambda_handler(event, context):
    print(event)
    print(context)

    jira_url = os.environ["JIRA_URL"]+event["jira"]["key"]
    print(jira_url)
    return {
        "statusCode": 200,
        "endpoint": f"sending to {jira_url}",
        "data": event["jira"]["data"]
    }