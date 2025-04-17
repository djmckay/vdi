import hashlib
import hmac
import json
import os

def compare_signature(given_signature, payload, secret):

    hash_object = hmac.new(
        secret.encode("utf-8"),
        msg=payload.encode("utf-8"),
        digestmod=hashlib.sha256,
    )
    calculated_signature = "sha256=" + hash_object.hexdigest()

    return hmac.compare_digest(calculated_signature, given_signature)


def lambda_handler(event, context):

    secret = os.environ["API_SECRET"]

    payload = json.loads(event["body"])
    print("get from header field X-Hub-Signature")

    try:
        # Extract the JWT token from the Authorization header
        token = event['headers'].get('X-Hub-Signature')
        print(token)

        # API Gateway method ARN
        method_arn = event['methodArn']

        # Decision logic
        if  compare_signature(token, payload, secret):
            return generate_policy('user', 'Allow', method_arn, {'group': "Jira"})
        else:
            return generate_policy('user', 'Deny', method_arn)

    except Exception as e:
        print(f"Error in authorizer: {e}")
        return generate_policy('user', 'Deny', event.get('methodArn', '*'))

def generate_policy(principal_id, effect, resource, context=None):

    #Generate an IAM policy for API Gateway.

    policy = {
        'principalId': principal_id,
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Action': 'execute-api:Invoke',
                    'Effect': effect,
                    'Resource': resource
                }
            ]
        }
    }

    if context:
        policy['context'] = context

    return policy