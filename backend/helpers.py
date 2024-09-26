import os
import tiktoken
from dotenv import load_dotenv
from passlib.context import CryptContext
from typing import Literal

# Load env variables
load_dotenv()

# Set context for password hashing
password_context = CryptContext(
    schemes                         = ["sha256_crypt"],
    sha256_crypt__default_rounds    = int(os.getenv('SHA256_ROUNDS')),
    deprecated                      = "auto"
)

# Helper function to hash passwords
def get_password_hash(password: str) -> str:
    '''Helper function to return hashed passwords'''

    return password_context.hash(password)


# Helper function to verify passwords
def verify_password(plain_password: str, hashed_password: str) -> bool:
    '''Helper function to verify passwords'''

    return password_context.verify(plain_password, hashed_password)


# Helper function to count tokens
def count_tokens(text: str) -> int:
    '''Helper function to count tokens for the GPT-4o model'''

    encoding = tiktoken.encoding_for_model("gpt-4o")
    return len(encoding.encode(text))


# Helper function to provide rectification strings
def rectification_helper() -> Literal:
    '''Helper function to provide rectification strings'''

    return "The answer you provided is incorrect. I have attached the question and the steps to find the correct answer for the question. Please perform them and report the correct answer."


# Helper function to generate response restriction
def generate_restriction(final_answer: str, incorrect_response: bool = False) -> str:
    '''Helper function to generate response restriction'''

    words = final_answer.split()
    if len(words) <= 10:
        return f"Restrict your response to {len(words)} words only."
    elif final_answer.replace(" ", "").isdigit():
        return "Provide only numerical values in your response."
    else:
        return ""