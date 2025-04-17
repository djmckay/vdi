import json
import boto3
import os
import pg8000
from botocore.exceptions import BotoCoreError, NoCredentialsError


def get_db_credentials():
    """Retrieve database credentials from AWS Secrets Manager."""
    secret_name = os.environ["DB_SECRET"]
    print(secret_name)
    client = boto3.client("secretsmanager")
    try:
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response["SecretString"])
    except (BotoCoreError, NoCredentialsError) as e:
        print(f"Error retrieving secret: {e}")
        return None


def connect_to_db():

        creds = get_db_credentials()
        print(creds['dbname'])
        if not creds:
            return

        try:
            print("Connecting to database...")
            conn = pg8000.connect(
                user=creds["username"],
                password=creds["password"],
                host=creds["host"],
                port=int(creds["port"]),
                database=creds["dbname"]
            )
        except Exception as e:
            print(f"Database error: {e}")
            return

        print("Connected to database")
        return conn

