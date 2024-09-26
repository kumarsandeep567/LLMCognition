from mysql.connector import Error
from dotenv import load_dotenv
from google.cloud import storage
from google.oauth2 import service_account
import logging
import mysql.connector
import pandas as pd
import ast
import os

# Logger function
logging.basicConfig(level = logging.INFO, format = '%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def execute_create_query(conn):
    logger.info("Creating tables")
    try:
        drop_features_table_query = "DROP TABLE IF EXISTS gaia_features;"
        drop_annotation_table_query = "DROP TABLE IF EXISTS gaia_annotations;"
        create_features_table_query = """
        CREATE TABLE gaia_features(
            task_id VARCHAR(255) PRIMARY KEY,
            question TEXT,
            level INT,
            final_answer VARCHAR(255),
            file_name VARCHAR(255),
            file_path VARCHAR(255)
        );
        """
        create_annotation_table_query = """
        CREATE TABLE gaia_annotations(
            task_id VARCHAR(255) PRIMARY KEY,
            steps TEXT,
            number_of_steps VARCHAR(255),
            time_taken VARCHAR(255),
            tools TEXT,
            number_of_tools VARCHAR(255),
            FOREIGN KEY (task_id) REFERENCES gaia_features(task_id)
        );
        """

        cursor = conn.cursor()
        cursor.execute(drop_features_table_query)
        cursor.execute(create_features_table_query)
        cursor.execute(drop_annotation_table_query)
        cursor.execute(create_annotation_table_query)
        logger.info("\nTable gaia_features created successfully\n")
        logger.info("Table gaia_annotations created successfully\n")
    except Exception as e:
        print(f"Error creating table: {e}")
        raise e

def execute_select_query(conn):
    logger.info("Selecting data from tables")

    # Queries
    features_query = 'SELECT * FROM gaia_features;'
    annotations_query = 'SELECT * FROM gaia_annotations;'

    cursor = conn.cursor()

    cursor.execute(features_query)
    features_results = cursor.fetchall()
    logger.info("Features query executed successfully.")

    cursor.execute(annotations_query)
    annotations_results = cursor.fetchall()
    logger.info("Annotations query executed successfully.")

    logger.info("Features Query Results:")
    for row in features_results:
        logger.info(row)
    
    logger.info("\nAnnotations Query Results:")
    for row in annotations_results:
        logger.info(row)

def execute_insert_query(conn, formatted_data, formatted_metadata):
    logger.info("Selecting data from tables")

    insert_features_table_query = """
    INSERT INTO gaia_features (task_id, question, level, final_answer, file_name, file_path)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    insert_annotation_table_query = """
    INSERT INTO gaia_annotations (task_id, steps, number_of_steps, time_taken, tools, number_of_tools)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    cursor = conn.cursor()
    for item in formatted_data:
        cursor.execute(insert_features_table_query, (item['task_id'], item['question'], item['level'], item['final_answer'], item['file_name'], item['file_path']))
    logger.info("Insertion into gaia_features done\n")
    for item in formatted_metadata:
        cursor.execute(insert_annotation_table_query, (item['task_id'], item['steps'], item['number_of_steps'], item['time_taken'], item['tools'], item['number_of_tools']))
    logger.info("Insertion into gaia_annotations done\n")
    logger.info("Insert statement executed successfully")

def connect_to_mysql():
    try:
        connection = mysql.connector.connect(
            host = os.getenv("MYSQL_HOSTNAME"),
            database = os.getenv("MYSQL_DATABASE"),
            user = os.getenv("MYSQL_ROOT"),
            password = os.getenv("MYSQL_ROOT_PASSWORD")
        )

        if connection.is_connected():
            logger.info("Connected to MySQL database successfully")
            return connection
    except Error as e:
        logger.info(f"Error as {e}")
        raise e
    
def download_csv_from_gcs(bucket_name, blob_name, local_file_path, creds_file_path):
    # Download CSV file from GCS
    logger.info("In function to download CSV file from GCS")

    creds = service_account.Credentials.from_service_account_file(creds_file_path)
    client = storage.Client(credentials = creds)
    bkt = client.bucket(bucket_name)
    blob = bkt.blob(blob_name)
    blob.download_to_filename(local_file_path)
    logger.info(f"Downloaded {blob_name} from GCS bucket {bucket_name} to {local_file_path}")

def get_file_paths(bucket_name, creds_file_path, gcp_folder_path):
    # Retrieve file names from GCS bucket

    storage_client = storage.Client.from_service_account_json(creds_file_path)
    blobs = storage_client.list_blobs(bucket_name, prefix = gcp_folder_path)
    file_path_dict = {os.path.basename(blob.name): f"/{bucket_name}/{blob.name}" for blob in blobs if blob.name.startswith(gcp_folder_path)}
    return file_path_dict



def format_csv_data(df, file_paths_dict):
    logger.info("Formatting data inside CSV file")
    formatted_data = []
    formatted_metadata = []
    
    for index, row in df.iterrows():
        file_name = None if ((pd.isna(row['file_name'])) or (row['file_name'] == '')) else row['file_name'].strip('"')
        file_path = file_paths_dict.get(file_name)

        formatted_row = {
            'task_id': row["task_id"].strip('"'),
            'question': row["Question"].strip('"'),
            'level': int(row["Level"]),
            'final_answer': row['Final answer'].strip('"'),
            'file_name': file_name,
            'file_path': file_path
        }
        formatted_data.append(formatted_row)

        metadata_str = row['Annotator Metadata']
        metadata = ast.literal_eval(metadata_str)

        # Replace final_answer in steps with an empty string
        if 'final_answer' in formatted_row:
            final_answer = formatted_row['final_answer']
            metadata['Steps'] = metadata['Steps'].replace(final_answer, '') 


        formatted_metadata_row = {
            'task_id': row['task_id'].strip('"'),
            'steps' : metadata['Steps'],
            'number_of_steps' : metadata['Number of steps'],
            'time_taken' : metadata['How long did this take?'],
            'tools' : metadata['Tools'],
            'number_of_tools' : metadata['Number of tools']
        }
        formatted_metadata.append(formatted_metadata_row)
    logger.info("Features and metadata formatting done")


    return formatted_data, formatted_metadata

def main():
    logger.info("Inside main function")
    load_dotenv()
    conn = connect_to_mysql()
    try:

        # Environment variables
        bucket_name = os.getenv("BUCKET_NAME")
        blob_name = os.getenv("GCP_CSV_PATH") + os.getenv("CSV_FILENAME")
        local_csv_path = os.getenv("CSV_FILENAME")
        gcp_folder_path = os.getenv("GCP_FILES_PATH")
        creds_file_path = os.getenv("GCS_CREDENTIALS_PATH")

        file_paths_dict = get_file_paths(bucket_name, creds_file_path, gcp_folder_path)

        # Download the CSV file from GCS
        download_csv_from_gcs(bucket_name, blob_name, local_csv_path, creds_file_path)

        # Load CSV data into DataFrame
        df = pd.read_csv(local_csv_path)

        formatted_data, formatted_metadata = format_csv_data(df, file_paths_dict)

        # Execute Queries
        execute_create_query(conn)
        execute_select_query(conn)
        execute_insert_query(conn, formatted_data, formatted_metadata)
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