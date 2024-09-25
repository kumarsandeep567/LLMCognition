import os
import time
import json
import logging
import mysql.connector
from openai import OpenAI
from fastapi import FastAPI
from http import HTTPStatus
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Optional, Any
from mysql.connector import Error
from fastapi.middleware.cors import CORSMiddleware

# Custom libraries
from helpers import get_password_hash, verify_password, count_tokens, generate_restriction

# ============================= FastAPI : Begin =============================
# Initialize FastAPI instance
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins       = ["*"],
    allow_credentials   = True,
    allow_methods       = ["*"],
    allow_headers       = ["*"],
)
# ============================= FastAPI : End ===============================


# Load env variables
load_dotenv()

# Setup OpenAI API key
openai_client = OpenAI(
    api_key         = os.getenv("OPENAI_API"),
    project         = os.getenv("PROJECT_ID"),
    organization    = os.getenv("ORGANIZATION_ID")
)


# ============================= Logger : Begin =============================

# Initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Log to console (dev only)
if os.getenv('APP_ENV') == "development":
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Also log to a file
file_handler = logging.FileHandler(os.getenv('LOG_FILE'))
file_handler.setFormatter(formatter)
logger.addHandler(file_handler) 

# ============================= Logger : End ===============================


# ====================== Application service : Begin ======================

# Pydantic models for request body validation
class UserRegister(BaseModel):
    first_name: str
    last_name: str
    phone: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class PasswordReset(BaseModel):
    first_name: str
    last_name: str
    phone: str
    email: str
    new_password: str

class QueryGPT(BaseModel):
    task_id: str


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
            logger.info("Database - Connection to the database was opened")
            return conn
        
        except (Error, IOError) as error:
            if attempt == attempts:
                # Ran out of attempts
                logger.error(f"Database - Failed to connect to database : {error}")
                return None
            else:
                logger.warning(f"Database - Connection failed: {error} - Retrying {attempt}/{attempts} ...")
                
                # Delay the next attempt
                time.sleep(delay ** attempt)
                attempt += 1
    
    return None


# Route for FastAPI Health check
@app.get("/health")
def health() -> dict[str, Any]:
    '''Check if the FastAPI application is setup and running'''

    logger.info("GET - /health request received")
    return {
        'status'    : HTTPStatus.OK,
        'type'      : "string",
        'message'   : "You're viewing a page from FastAPI"
    }


# Route for database health check
@app.get("/database")
def dbhealth() -> dict[str, Any]:
    '''Check if FastAPI can communicate with the database'''

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
        logger.info("Database - Connection to the database was closed")
    
    return response


# Route for user registration
@app.post("/register")
def register(user: UserRegister) -> dict[str, Any]:
    '''Sign up new users to the application'''

    logger.info("POST - /register request received")
    conn = create_connection()

    if conn is None:
        return {
            'status'    : HTTPStatus.SERVICE_UNAVAILABLE,
            'type'      : "string",
            'message'   : "Database not found :("
        }

    if conn and conn.is_connected():
        with conn.cursor(dictionary = True) as cursor:
            try:
                
                # Check if email already exists
                logger.info("SQL - Running a SELECT statement")
                cursor.execute("SELECT * FROM users WHERE email = %s", (user.email,))
                logger.info("SQL - SELECT statement complete")
                
                if cursor.fetchone():
                    conn.close()
                    logger.info("Database - Connection to the database was closed")

                    return {
                        'status'    : HTTPStatus.BAD_REQUEST,
                        'type'      : "string",
                        'message'   : "Email already registered. Please login."
                    }

                # Hash the password
                hashed_password = get_password_hash(user.password)

                # Insert the new user in the database
                logger.info("SQL - Running an INSERT statement")
                query = """
                INSERT INTO users (first_name, last_name, phone, email, password)
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    user.first_name, 
                    user.last_name, 
                    user.phone, 
                    user.email, 
                    hashed_password
                ))
                conn.commit()
                logger.info("SQL - INSERT statement complete")

                new_user_id = cursor.lastrowid
                logger.info(f"New user registered with ID: {new_user_id}")

                response = {
                    "status"    : HTTPStatus.OK,
                    'type'      : "string",
                    "message"   : "User registered successfully",
                    "user_id"   : new_user_id
                }

            except Exception as exception:
                logger.error("Error: register() encountered an error")
                logger.error(exception)
                response = {
                    "status"    : HTTPStatus.INTERNAL_SERVER_ERROR,
                    'type'      : "string",
                    "message"   : "New user could not be registered. Something went wrong.",
                }
                
            finally:
                conn.close()
                logger.info("Database - Connection to the database was closed")
        
        return response


# Route for user login
@app.post("/login")
def login(user: UserLogin) -> dict[str, Any]:
    '''Sign in an existing user'''

    logger.info("POST - /login request received")
    conn = create_connection()

    if conn is None:
        return {
            'status'    : HTTPStatus.SERVICE_UNAVAILABLE,
            'type'      : "string",
            'message'   : "Database not found :("
        }

    if conn and conn.is_connected():
        with conn.cursor(dictionary = True) as cursor:
            try:

                # Fetch user by email
                logger.info("SQL - Running a SELECT statement")
                cursor.execute("SELECT * FROM users WHERE email = %s", (user.email,))
                logger.info("SQL - SELECT statement complete")

                db_user = cursor.fetchone()

                if db_user is None:
                    conn.close()
                    logger.info("Database - Connection to the database was closed")

                    return {
                        'status'    : HTTPStatus.NOT_FOUND,
                        'type'      : "string",
                        'message'   : "User not found"
                    }

                # Verify password
                if not verify_password(user.password, db_user['password']):
                    response = {
                        'status'    : HTTPStatus.UNAUTHORIZED,
                        'type'      : "string",
                        'message'   : "Invalid email or password"
                    }
                else:
                    logger.info(f"User logged in: {db_user['user_id']}")
                    response =  {
                        "status"    : HTTPStatus.OK,
                        'type'      : "string",
                        "message"   : "Login successful",
                        "user_id"   : db_user['user_id']
                    }

            except Exception as exception:
                logger.error("Error: login() encountered an error")
                logger.error(exception)
                response = {
                    "status"    : HTTPStatus.INTERNAL_SERVER_ERROR,
                    'type'      : "string",
                    "message"   : "User could not be logged in. Something went wrong.",
                }
            finally:
                conn.close()
                logger.info("Database - Connection to the database was closed")

        return response


# Route for password reset
@app.post("/resetpassword")
def reset_password(reset_data: PasswordReset) -> dict[str, Any]:
    '''Allow users to set a new password if correct details are provided'''

    logger.info("POST - /resetpassword request received")
    conn = create_connection()

    if conn is None:
        return {
            'status'    : HTTPStatus.SERVICE_UNAVAILABLE,
            'type'      : "string",
            'message'   : "Database not found :("
        }

    if conn and conn.is_connected():
        with conn.cursor(dictionary = True) as cursor:
            try:

                # Check if user exists and all provided details match
                logger.info("SQL - Running a SELECT statement")
                query = """
                SELECT * FROM users 
                WHERE first_name = %s 
                AND last_name = %s 
                AND phone = %s 
                AND email = %s
                """
                cursor.execute(query, (
                    reset_data.first_name, 
                    reset_data.last_name, 
                    reset_data.phone, 
                    reset_data.email
                ))
                logger.info("SQL - SELECT statement complete")
                user = cursor.fetchone()

                if user is None:
                    conn.close()
                    logger.info("Database - Connection to the database was closed")

                    return {
                        'status'    : HTTPStatus.UNAUTHORIZED,
                        'type'      : "string",
                        'message'   : "User not found or details do not match"
                    }
                    
                # Hash the new password
                hashed_password = get_password_hash(reset_data.new_password)

                # Update the password
                logger.info("SQL - Running a UPDATE statement")
                update_query = "UPDATE users SET password = %s WHERE user_id = %s"
                cursor.execute(update_query, (hashed_password, user['user_id']))
                conn.commit()
                logger.info("SQL - UPDATE statement complete")

                logger.info(f"Password reset successful for user ID: {user['user_id']}")

                response = {
                    "status"    : HTTPStatus.OK,
                    'type'      : "string",
                    "message"   : "Password reset successful"
                }

            except Exception as exception:
                logger.error("Error: reset_password() encountered an error")
                logger.error(exception)
                response = {
                    "status"    : HTTPStatus.INTERNAL_SERVER_ERROR,
                    'type'      : "string",
                    "message"   : "Password could not be reset. Something went wrong.",
                }

            finally:
                conn.close()
                logger.info("Database - Connection to the database was closed")

        return response


# Route for listing prompts
@app.get("/listprompts")
@app.get("/listprompts/{count}")
def list_prompts(count: Optional[int] = None) -> dict[str, Any]:
    '''Fetch "x" number of prompts from the database'''

    if count is None:
        logger.info("GET - /listprompts request received")
        count = 5
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
        with conn.cursor(dictionary = True) as cursor:
            try:
                logger.info("SQL - Running a SELECT statement")

                # Fetch the task_id, question from the table
                query = f"SELECT `task_id`, `question` FROM `gaia_features` LIMIT {count}"
                result = cursor.execute(query)
                rows = cursor.fetchall()

                response = {
                    'status'    : HTTPStatus.OK,
                    'type'      : "json",
                    'message'   : rows,
                    'length'    : count
                }

                logger.info("SQL - SELECT statement complete")
                conn.close()
                logger.info("Database - Connection to the database was closed")

                return response

            except Exception as exception:
                logger.error("Error: list_prompts() encountered a SQL error")
                logger.error(exception)

            finally:
                conn.close()
                logger.info("Database - Connection to the database was closed")
    
        return {
            'status'    : HTTPStatus.INTERNAL_SERVER_ERROR,
            'type'      : "string",
            'message'   : "Could not fetch the list of prompts. Something went wrong."
        }


# Route for fetching all details about a prompt
@app.get("/loadprompt/{task_id}")
def loadprompt(task_id: str) -> dict[str, Any]:
    '''Load all information from the database regarding the given prompt'''

    logger.info(f"GET - /loadprompt/{task_id} request received")
    conn = create_connection()

    if conn is None:
        return {
            'status'    : HTTPStatus.SERVICE_UNAVAILABLE,
            'type'      : "string",
            'message'   : "Database not found :("
        }

    if conn and conn.is_connected():
        with conn.cursor(dictionary = True) as cursor:
            try:

                # Fetch the task_id, question, level, final_answer, file_name 
                logger.info("SQL - Running a SELECT statement")
                query = """
                SELECT task_id, question, level, final_answer, file_name 
                FROM gaia_features
                WHERE task_id = %s
                """
                result = cursor.execute(query, (task_id,))
                record = cursor.fetchone()
                logger.info("SQL - SELECT statement complete")

                if record is None:
                    conn.close()
                    logger.info("Database - Connection to the database was closed")

                    return {
                        'status'    : HTTPStatus.NOT_FOUND,
                        'type'      : "string",
                        'message'   : f"Could not fetch the details for the given task_id (not found) {task_id}"
                    }

                conn.close()
                logger.info("Database - Connection to the database was closed")

                return {
                    'status'    : HTTPStatus.OK,
                    'type'      : "json",
                    'message'   : record
                }

            except Exception as exception:
                logger.error("Error: list_prompts() encountered a SQL error")
                logger.error(exception)

            finally:
                conn.close()
                logger.info("Database - Connection to the database was closed")
    
        return {
            'status'    : HTTPStatus.INTERNAL_SERVER_ERROR,
            'type'      : "string",
            'message'   : "Could not fetch details for the prompt. Something went wrong."
        }


# Route for fetching annotation details for a prompt
@app.get("/getannotation/{task_id}")
def getannotation(task_id: str) -> dict[str, Any]:
    '''Load the annotation from the database regarding the given prompt'''

    logger.info(f"GET - /loadprompt/{task_id} request received")
    conn = create_connection()

    if conn is None:
        return {
            'status'    : HTTPStatus.SERVICE_UNAVAILABLE,
            'type'      : "string",
            'message'   : "Database not found :("
        }

    if conn and conn.is_connected():
        with conn.cursor(dictionary = True) as cursor:
            try:

                # Fetch the final_answer for the task_id
                logger.info("SQL - Running a SELECT statement")
                query = """SELECT final_answer FROM gaia_features WHERE task_id = %s"""

                result = cursor.execute(query, (task_id,))
                final_answer = cursor.fetchone()
                logger.info("SQL - SELECT statement complete")

                if final_answer is None:
                    conn.close()
                    logger.info("Database - Connection to the database was closed")

                    return {
                        'status'    : HTTPStatus.NOT_FOUND,
                        'type'      : "string",
                        'message'   : f"Could not fetch the details for the given task_id (not found) {task_id}"
                    }

                # Fetch the steps for the task_id
                logger.info("SQL - Running a SELECT statement")
                query = """SELECT Steps FROM annotation_features WHERE task_id = %s"""

                result = cursor.execute(query, (task_id,))
                prompt_steps = cursor.fetchone()
                logger.info("SQL - SELECT statement complete")

                if prompt_steps is None:
                    conn.close()
                    logger.info("Database - Connection to the database was closed")

                    return {
                        'status'    : HTTPStatus.NOT_FOUND,
                        'type'      : "string",
                        'message'   : f"Could not fetch the annotation steps for the given task_id (not found) {task_id}"
                    }
                
                filtered_prompt = prompt_steps['Steps'].replace(final_answer['final_answer'], '___')

                conn.close()
                logger.info("Database - Connection to the database was closed")

                return {
                    'status'    : HTTPStatus.OK,
                    'type'      : "string",
                    'message'   : filtered_prompt
                }

            except Exception as exception:
                logger.error("Error: list_prompts() encountered a SQL error")
                logger.error(exception)

            finally:
                conn.close()
                logger.info("Database - Connection to the database was closed")
    
        return {
            'status'    : HTTPStatus.INTERNAL_SERVER_ERROR,
            'type'      : "string",
            'message'   : "Could not fetch details for the prompt. Something went wrong."
        }
    

def update_analytics(data: dict) -> bool:
    '''Save GPT-4's response and some other data to the database'''

    logger.info("INTERNAL - request to save response data to database received")
    conn = create_connection()
    response = False

    if conn and conn.is_connected():
        with conn.cursor(dictionary = True) as cursor:
            try:

                # Update the analytics 
                # Insert the new user in the database
                logger.info("SQL - Running an INSERT statement")
                query = """
                INSERT INTO analytics (user_id, task_id, gpt_response, tokens_per_text_prompt)
                VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query, (
                    data['user_id'],
                    data['task_id'],
                    data['gpt_response'],
                    data['token_count']
                ))
                conn.commit()
                logger.info("SQL - INSERT statement complete")
                response = True         

            except Exception as exception:
                logger.error("Error: update_analytics() encountered an error")
                logger.error(exception)
                
            finally:
                conn.close()
                logger.info("Database - Connection to the database was closed")
    
    return response


# Route for querying GPT
@app.post("/querygpt")
async def query_gpt(query: QueryGPT) -> dict[str, Any]:
    '''Forward the question to OpenAI GPT4 and evaluate based on GAIA Benchmark'''

    logger.info(f"POST - /querygpt/{query.task_id} request received")
    
    try:
        
        # Get the prompt, apply restriction wherever needed, and send to GPT
        prompt = loadprompt(query.task_id)

        if prompt and prompt['status'] == HTTPStatus.OK:
            
            token_count = count_tokens(prompt['message']['question'])
            restriction = generate_restriction(prompt['message']['final_answer'])
            full_question = f"{prompt['message']['question']} {restriction}".strip()

            # Send question to GPT
            logger.info("GPT - Sending a ChatCompletion request")
            response = openai_client.chat.completions.create(
                model = "gpt-4o",
                temperature = 0.6,
                messages = [
                    {"role": "system", "content": "You are a helpful assistant that obeys the instructions given and provides the correct answers for any questions provided."},
                    {"role": "user", "content": full_question}
                ]
            )

            logger.info("GPT - ChatCompletion request complete")
            gpt_response = response.choices[0].message.content

            # Save to analytics table
            response_data = {
                "user_id"       : 6,
                "task_id"       : prompt['message']['task_id'],
                "token_count"   : token_count,
                "gpt_response"  : gpt_response
            }

            if update_analytics(response_data):
                logger.info("INTERNAL - analytics data saved to database")
            else:
                logger.error("INTERNAL - Failed to save analytics data to database")

            json_response = {
                "status"        : HTTPStatus.OK,
                "task_id"       : prompt['message']['task_id'],
                "question"      : full_question,
                "level"         : prompt['message']['level'],
                "file_name"     : prompt['message']['file_name'],
                "token_count"   : token_count,
                "gpt_response"  : gpt_response
            }

            # Get the annotation and append it to the json response
            logger.info(f"INTERNAL - Fetching annotation for task_id {prompt['message']['task_id']}")
            annotation = getannotation(prompt['message']['task_id'])

            if annotation["status"] == HTTPStatus.OK:
                json_response["annotation_steps"] = annotation["message"]

            return json_response
    
    except Exception as exception:
        logger.error("Error: querygpt() encountered a an error")
        logger.error(exception)

    return {
        'status'    : HTTPStatus.INTERNAL_SERVER_ERROR,
        'type'      : "string",
        'message'   : "Could not send prompt to GPT. Something went wrong."
    }


# ====================== Application service : End ======================


# Tokenize the prompts that you send to gpt4 in fastapi
# refer https://platform.openai.com/tokenizer

# Use openai's tiktoken package to achieve this
# referhttps://github.com/openai/tiktoken

# Add a price warning in fastapi
# Refer pricing charts based on tokens