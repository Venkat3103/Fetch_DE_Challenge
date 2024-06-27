import boto3
import hashlib
import json
import logging
import psycopg2
from datetime import datetime, timezone
from typing import Optional, Dict, Any

# Constants
QUEUE_URL = "http://localhost:4566/000000000000/login-queue"
POSTGRES_CONN_PARAMS = "dbname=postgres user=postgres password=postgres host=localhost port=5432"

# Setting up logging to track events
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_connection() -> Optional[psycopg2.extensions.connection]:
    """
    Create and return a new postgres database connection.
    
    Returns:
        Optional[psycopg2.extensions.connection]: A new database connection if successful, None otherwise.
    """
    try:
        conn = psycopg2.connect(POSTGRES_CONN_PARAMS)
        logger.info("Connection to the database is successful.")
        return conn
    except Exception as e:
        logger.error(f"An error occurred while connecting to the database: {e}")
        return None

def hash_pii(data: str) -> str:
    """
    Function to Hash PII data using SHA-256 to ensure duplicates are identifiable.
    
    Args:
        data (str): The PII data to hash.
        
    Returns:
        str: The SHA-256 hash of the data.
    """
    return hashlib.sha256(data.encode()).hexdigest()

def transform_data(json_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Transforms JSON data for database insertion by hashing PII and flattening.
    
    Args:
        json_data (Dict[str, Any]): The JSON data to be transformed.
    
    Returns:
        Optional[Dict[str, Any]]: The transformed data for database insertion, or None if an error is encountered.
    """

    # As per the schema, these fields must be present in the json data obtained from the queue
    required_fields = ["device_id", "ip", "user_id", "device_type", "app_version", "locale"]
    if not all(field in json_data for field in required_fields):
        error_msg = f"Missing fields in data: {json_data}"
        logger.error(error_msg)
        log_error_data(json_data, error_msg)
        return None

    try:
        return {
            "user_id": json_data["user_id"],
            "device_type": json_data["device_type"],
            "masked_ip": hash_pii(json_data["ip"]),
            "masked_device_id": hash_pii(json_data["device_id"]),
            "locale": json_data["locale"],
            "app_version": json_data["app_version"], 
            "create_date": datetime.now(timezone.utc).date()
        }
    except Exception as e:
        error_msg = f"Error processing data: {e} - Data: {json_data}"
        logger.error(error_msg)

        # when an error is encountered, the log_error_data function is called and the record is inserted in the error log table
        log_error_data(json_data, error_msg)
        return None

def log_error_data(json_data: Dict[str, Any], error_msg: str):
    """
    Logs error data in the message queue to a separate errors log table.
    
    Args:
        json_data (Dict[str, Any]): The JSON data that caused the error.
        error_msg (str): The error message associated with the error.
    """
    conn = create_connection()
    if conn:
        with conn.cursor() as cursor:
            # Check and create the error_log_table table if it does not exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS error_log_table (
                    error_id SERIAL PRIMARY KEY,
                    error_message TEXT NOT NULL,
                    error_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    json_data JSONB NOT NULL
                );
            """)
            # Insert the error log
            cursor.execute("""
                INSERT INTO error_log_table (error_message, json_data)
                VALUES (%s, %s)
            """, (error_msg, json.dumps(json_data)))
            conn.commit()
        conn.close()

def run_pipeline(sqs: boto3.Session.client):
    """
    Function to ingest SQS queue message into the PostgreSQL database.
    
    Args:
        sqs (boto3.Session.client): The SQS client object to receive messages from.
    """
    conn = create_connection()
    
    if conn:

        # It was identified that the app_version is defined as an int in the schema while the message queue contains vesions in n.n.n format. Hence schema altered 
        # to convert app_version type to string (varchar) 
        with conn.cursor() as cursor:
            cursor.execute("""
                ALTER TABLE user_logins ALTER COLUMN app_version TYPE varchar;
            """)
            conn.commit()

        while True:

            # Long polling is used here. 10 messages are read every 20 seconds. This is a random value that I have chosen (since we only have 100 values in the queue)
            response = sqs.receive_message(
                QueueUrl=QUEUE_URL, AttributeNames=["All"], MaxNumberOfMessages=10, WaitTimeSeconds=20
            )
            messages = response.get("Messages", [])
            if not messages:
                logger.info("No more messages to read. Queue empty")
                break

            for msg in messages:
                json_data = json.loads(msg['Body'])
                transformed_data = transform_data(json_data)
                if transformed_data:
                    store_messages_in_db(conn, [transformed_data])
                else:
                    logger.info(f"Invalid or incomplete message skipped: {msg}")
        conn.close()

def store_messages_in_db(conn: psycopg2.extensions.connection, data_entries: list):
    """
    Stores a list of data entries into the PostgreSQL database.
    
    Args:
        conn (psycopg2.extensions.connection): The database connection object.
        data_entries (list): The list of data entries to store.
    """
    with conn.cursor() as cursor:
        for entry in data_entries:
            try:
                cursor.execute("""
                    INSERT INTO user_logins (user_id, device_type, masked_ip, masked_device_id, locale, app_version, create_date)
                    VALUES (%(user_id)s, %(device_type)s, %(masked_ip)s, %(masked_device_id)s, %(locale)s, %(app_version)s, %(create_date)s)
                """, entry)
                conn.commit()
            except Exception as e:
                logger.error("Failed to insert data:", str(e))
                conn.rollback()

if __name__ == "__main__":

    # Creating a client with boto3 for sqs. Using dummy configuration for AWS credentials
    sqs = boto3.client(
        "sqs",
        endpoint_url="http://localhost:4566",
        region_name="us-east-1",
        aws_access_key_id="test",
        aws_secret_access_key="test",
    )
    run_pipeline(sqs)
