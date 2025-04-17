import hashlib
import hmac
import json
import os
import boto3

def compare_signature(given_signature, payload, secret):

    hash_object = hmac.new(
        secret.encode("utf-8"),
        msg=payload.encode("utf-8"),
        digestmod=hashlib.sha256,
    )
    calculated_signature = "sha256=" + hash_object.hexdigest()

    print("calculated_signature=", calculated_signature)
    return hmac.compare_digest(calculated_signature, given_signature)


def lambda_handler(event, context):

    secret = os.environ["API_SECRET"]

    payload = event["body"]
    print("get from header field X-Hub-Signature")

    try:
        # Extract the JWT token from the Authorization header
        token = event['headers'].get('X-Hub-Signature'.lower())
        print(token)

        # Decision logic
        if  compare_signature(token, payload, secret):
            return send_to_sqs(event, context)
        else:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Not Authorized"})
            }

    except Exception as e:
        print(f"Error in authorizer: {e}")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Not Authorized"})
        }


def send_to_sqs(event, context):
    sqs = boto3.client("sqs")
    QUEUE_URL = os.environ["QUEUE_URL"]

    try:
        # Parse body from API Gateway
        body = event.get("body")
        headers = event.get("headers", {})
        webhook_id = headers.get("X-Atlassian-Webhook-Identifier")

        if not body:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing body in request"})
            }

        message = {
            "headers": {
                "X-Atlassian-Webhook-Identifier": webhook_id
            },
            "body": json.loads(body)
        }

        # Send to SQS
        response = sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps(message)
        )

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Payload sent to SQS",
                "messageId": response["MessageId"]
            })
        }

    except Exception as e:
        print(f"Error sending to SQS: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
