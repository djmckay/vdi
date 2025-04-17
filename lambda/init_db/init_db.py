import json
import db


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


def create_tables(conn):
    """Create required tables in the Aurora PostgreSQL database."""
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processed_webhooks (
                webhook_id TEXT PRIMARY KEY,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jira_issues (
                issue_key TEXT PRIMARY KEY,
                summary TEXT,
                status TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

    conn.commit()


def lambda_handler(event, context):
    """AWS Lambda function entry point."""
    # creds = get_db_credentials()
    # print(creds['dbname'])
    # if not creds:
    #     return {"statusCode": 500, "body": "Failed to retrieve database credentials"}
    #
    try:
    #     print("Connecting to database...")
    #     conn = pg8000.connect(
    #         user=creds["username"],
    #         password=creds["password"],
    #         host=creds["host"],
    #         port=int(creds["port"]),
    #         database=creds["dbname"]
    #     )
    #     print("Connected to database")
        conn = db.connect_to_db()
        create_tables(conn)
        conn.close()
        return {"statusCode": 200, "body": "Database tables created successfully"}
    except Exception as e:
        print(f"Database error: {e}")
        return {"statusCode": 500, "body": f"Database setup failed: {str(e)}"}
