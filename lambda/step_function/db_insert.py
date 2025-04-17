import json
import pg8000
import boto3
import os
import db

# def get_db_credentials():
#     secret_name = os.environ["DB_SECRET"]
#     client = boto3.client("secretsmanager")
#     response = client.get_secret_value(SecretId=secret_name)
#     return json.loads(response["SecretString"])


def lambda_handler(event, context):
    # Extract SQS message body (Jira webhook payload)
    print(event)
    # for record in event:
    print(event)
    payload = event
    print(payload)
    issue_key = payload["issue"]["key"]
    issue_summary = payload["issue"]["fields"]["summary"]
    issue_status = payload["issue"]["fields"]["status"]

        # Get DB credentials
        # db_credentials = get_db_credentials()

        # Connect to Aurora PostgreSQL
        # conn = pg8000.connect(
        #     host=db_credentials["host"],
        #     dbname=db_credentials["dbname"],
        #     user=db_credentials["username"],
        #     password=db_credentials["password"],
        #     port=db_credentials["port"]
        # )
    conn = db.connect_to_db()
    cur = conn.cursor()
    cur.execute(
            """
            INSERT INTO jira_issues (issue_key, summary, status)
            VALUES (%s, %s, %s)
            ON CONFLICT (issue_key) DO UPDATE
            SET summary = EXCLUDED.summary, status = EXCLUDED.status;
            """,
            (issue_key, issue_summary, issue_status)
        )
    conn.commit()
    cur.close()
    conn.close()

    return {"statusCode": 200, "body": "Webhook processed successfully."}
