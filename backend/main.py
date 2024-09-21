import os
import time
import json
import logging
import mysql.connector
from fastapi import FastAPI
from http import HTTPStatus
from typing import Optional
from dotenv import load_dotenv
from mysql.connector import Error

# Initialize FastAPI instance
app = FastAPI()

# Load env variables
load_dotenv()

# Initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Log to console
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

# Also log to a file
file_handler = logging.FileHandler(os.getenv('LOG_FILE'))
file_handler.setFormatter(formatter)
logger.addHandler(file_handler) 


def create_connection(attempts = 3, delay = 2):
    '''Start a connection with the MySQL database'''

    # Database connection config
    config = {
        'user'              : os.getenv('DB_USER'),
        'password'          : os.getenv('DB_PASSWORD'),
        'host'              : os.getenv('DB_HOST'),
        'database'          : os.getenv('DB_NAME'),
        'raise_on_warnings' : True
    }

    # Attempt a reconnection routine
    attempt = 1
    
    while attempt <= attempts:
        try:
            conn = mysql.connector.connect(**config)
            logger.info("Connection to the database was opened")
            return conn
        
        except (Error, IOError) as error:
            if attempt == attempts:
                # Ran out of attempts
                logger.error(f"Failed to connect to database : {error}")
                return None
            else:
                logger.warning(f"Connection failed: {error} - Retrying {attempt}/{attempts} ...")
                
                # Delay the next attempt
                time.sleep(delay ** attempt)
                attempt += 1
    
    return None


# Route for FastAPI Health check
@app.get("/health")
def health() -> dict[str, str]:
    logger.info("GET - /health request received")
    return {
        'status'    : HTTPStatus.OK,
        'type'      : "string",
        'message'   : "You're viewing a page from FastAPI"
    }


# Route for database health check
@app.get("/database")
def dbhealth() -> dict[str, str]:
    logger.info("GET - /database request received")
    conn = create_connection()
    
    if conn is None:
        response = {
            'status'    : HTTPStatus.SERVICE_UNAVAILABLE,
            'type'      : "string",
            'message'   : "Database not found :("
        }
    else:
        response = {
            'status'    : HTTPStatus.OK,
            'type'      : "string",
            'message'   : "Connection with database established"
        }
        conn.close()
        logger.info("Connection to the database was closed")
    
    return response


# Route for listing prompts
@app.get("/listprompts")
@app.get("/listprompts/{count}")
def list_prompts(count: Optional[int] = None):
    if count is None:
        logger.info("GET - /listprompts request received")
    else:
        logger.info(f"GET - /listprompts/{count} request received")

    conn = create_connection()

    if conn is None:
        return {
            'status'    : HTTPStatus.SERVICE_UNAVAILABLE,
            'type'      : "string",
            'message'   : "Database not found :("
        }

    if conn and conn.is_connected():
        with conn.cursor() as cursor:
            try:
                logger.info("SQL - Running a SELECT statement")

                # Fetch the task_id, question from the table
                query = "SELECT `task_id`, `question` FROM `gaia_features` LIMIT 5"
                result = cursor.execute(query)
                rows = cursor.fetchall()
                
                # Get the column names from the cursor
                columns = [desc[0] for desc in cursor.description]

                # Convert rows to a list of dictionaries
                result_list = [dict(zip(columns, row)) for row in rows]

                # Convert to json
                json_result = json.dumps(result_list)

                response = {
                    'status'    : HTTPStatus.OK,
                    'type'      : "json",
                    'message'   : json_result
                }

                return response

            except Exception as exception:
                logger.error("Error: list_prompts() encountered a SQL error")
                logger.error(exception)
    
    return {
        'status'    : HTTPStatus.INTERNAL_SERVER_ERROR,
        'type'      : "string",
        'message'   : "An internal error occurred"
    }