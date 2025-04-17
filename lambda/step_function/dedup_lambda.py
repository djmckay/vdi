import json
import boto3
import os
import pg8000
import db
from botocore.exceptions import BotoCoreError, NoCredentialsError


# def get_db_credentials():
#     """Retrieve database credentials from AWS Secrets Manager."""
#     secret_name = os.environ["DB_SECRET"]
#     print(secret_name)
#     client = boto3.client("secretsmanager")
#     try:
#         response = client.get_secret_value(SecretId=secret_name)
#         return json.loads(response["SecretString"])
#     except (BotoCoreError, NoCredentialsError) as e:
#         print(f"Error retrieving secret: {e}")
#         return None


def lambda_handler(event, context):
    # Extract SQS message body (Jira webhook payload)
    body = ""
    print(event)
    print(context)
    # for record in event:
    payload = event
    print(payload)
    body = payload
    webhook_id = body["issue"]["id"]
    print(webhook_id)
    headers = payload.get("headers", {})
    print(headers.get("X-Atlassian-Webhook-Identifier"))
    # webhook_id = headers.get("X-Atlassian-Webhook-Identifier")

    if not webhook_id:
        return {"statusCode": 400, "body": "Missing Data."}

    # creds = get_db_credentials()
    # print(creds['dbname'])
    # if not creds:
    #     return {"statusCode": 500, "body": "Failed to retrieve database credentials"}

    try:
        conn = db.connect_to_db()
        # print("Connecting to database...")
        # conn = pg8000.connect(
        #     user=creds["username"],
        #     password=creds["password"],
        #     host=creds["host"],
        #     port=int(creds["port"]),
        #     database=creds["dbname"]
        # )
    except Exception as e:
        print(f"Database error: {e}")
        raise Exception(f"Database connection failed: {str(e)}")
        # return {"statusCode": 500, "body": f"Database connection failed: {str(e)}"}

    print("Connected to database")
    cur = conn.cursor()

    # Check if webhook ID already exists to prevent duplicate processing
    cur.execute("SELECT COUNT(*) FROM processed_webhooks WHERE webhook_id = %s", (webhook_id,))
    count = cur.fetchone()[0]
    print(count)
    if count > 0:
        raise Exception("This webhook has already been processed")
        # return {"statusCode": 200, "body": "Duplicate webhook ignored."}

    # Store webhook ID to prevent future duplicates
    cur.execute("INSERT INTO processed_webhooks (webhook_id) VALUES (%s)", (webhook_id,))
    cur.execute("SELECT COUNT(*) FROM processed_webhooks WHERE webhook_id = %s", (webhook_id,))
    count = cur.fetchone()[0]

    if count == 0:
        conn.rollback()
        raise Exception("Webhook ID does not exist")

    conn.commit()

    cur.close()
    conn.close()

    return {"statusCode": 200, "duplicate": "false"}
