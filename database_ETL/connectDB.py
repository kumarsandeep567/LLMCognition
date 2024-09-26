from mysql.connector import Error
from dotenv import load_dotenv
from google.cloud import storage
from google.oauth2 import service_account
import logging
import mysql.connector
import pandas as pd
import os

# Logger function
logging.basicConfig(level = logging.INFO, format = '%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def execute_create_query(conn):
    try:
        drop_table_query = "DROP TABLE IF EXISTS gaia_features;"
        create_table_query = """
        CREATE TABLE gaia_features(
            task_id VARCHAR(255),
            question TEXT,
            level INT,
            final_answer VARCHAR(255),
            file_name VARCHAR(255),
            file_path VARCHAR(255)
        );
        """

        cursor = conn.cursor()
        cursor.execute(drop_table_query)
        cursor.execute(create_table_query)
        print("Table gaia_features created successfully")
    except Exception as e:
        print(f"Error creating table: {e}")
        raise e

def execute_select_query(conn):
    query = 'SELECT * FROM gaia_features;'
    cursor = conn.cursor()
    cursor.execute(query)
    res = cursor.fetchall()
    print(f"The query execution results are:")
    for row in res:
        print(row)

def execute_insert_query(conn, formatted_data):
    insert_query = """
    INSERT INTO gaia_features (task_id, question, level, final_answer, file_name, file_path)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor = conn.cursor()
    for item in formatted_data:
        cursor.execute(insert_query, (item['task_id'], item['question'], item['level'], item['final_answer'], item['file_name'], item['file_path']))

    print("Insert statement executed successfully")

def connect_to_mysql():
    try:
        connection = mysql.connector.connect(
            host = os.getenv("MYSQL_HOSTNAME"),
            database = os.getenv("MYSQL_DATABASE"),
            user = os.getenv("MYSQL_ROOT"),
            password = os.getenv("MYSQL_ROOT_PASSWORD")
        )

        if connection.is_connected():
            print("Connected to MySQL database successfully")
            return connection
    except Error as e:
        print(f"Error as {e}")
        raise e
    
def download_csv_from_gcs(bucket_name, blob_name, local_file_path, creds_file_path):
    # Download CSV file from GCS

    creds = service_account.Credentials.from_service_account_file(creds_file_path)
    client = storage.Client(credentials = creds)
    bkt = client.bucket(bucket_name)
    blob = bkt.blob(blob_name)
    blob.download_to_filename(local_file_path)
    print(f"Downloaded {blob_name} from GCS bucket {bucket_name} to {local_file_path}")

def get_file_paths(bucket_name, creds_file_path, gcp_folder_path):
    # Retrieve file names from GCS bucket

    storage_client = storage.Client.from_service_account_json(creds_file_path)
    blobs = storage_client.list_blobs(bucket_name, prefix = gcp_folder_path)
    file_path_dict = {os.path.basename(blob.name): f"/{bucket_name}/{blob.name}" for blob in blobs if blob.name.startswith(gcp_folder_path)}
    return file_path_dict



def format_csv_data(df, file_paths_dict):
    formatted_data = []
    
    for index, row in df.iterrows():
        file_name = None if ((pd.isna(row['file_name'])) or (row['file_name'] == '')) else row['file_name'].strip('"')
        file_path = file_paths_dict.get(file_name)

        print(f"File Name: {file_name}, File Path: {file_path}")

        formatted_row = {
            'task_id': row["task_id"].strip('"'),
            'question': row["Question"].strip('"'),
            'level': int(row["Level"]),
            'final_answer': row['Final answer'].strip('"'),
            'file_name': file_name,
            'file_path': file_path
        }
        formatted_data.append(formatted_row)
    return formatted_data



def main():
    load_dotenv()
    conn = connect_to_mysql()
    try:

        # Environment variables
        # gaia_benchmark
        bucket_name = os.getenv("BUCKET_NAME")
        #csv_files/parsed_metadata.csv
        blob_name = os.getenv("GCP_CSV_PATH") + os.getenv("CSV_FILENAME")
        # parsed_metadata.csv
        local_csv_path = os.getenv("CSV_FILENAME")
        # files/
        gcp_folder_path = os.getenv("GCP_FILES_PATH")
        creds_file_path = os.getenv("GCS_CREDENTIALS_PATH")

        file_paths_dict = get_file_paths(bucket_name, creds_file_path, gcp_folder_path)

        # Download the CSV file from GCS
        download_csv_from_gcs(bucket_name, blob_name, local_csv_path, creds_file_path)

        # Load CSV data into DataFrame
        df = pd.read_csv(local_csv_path)

        formatted_data = format_csv_data(df, file_paths_dict)

        # Execute Queries
        execute_create_query(conn)
        execute_select_query(conn)
        execute_insert_query(conn, formatted_data)
        execute_select_query(conn)
        conn.commit()

    except Exception as e:
        logger.error(f"Error = {e}")
        raise e
    finally:
        conn.close()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Error while executing main function: {e}")
        raise(e)