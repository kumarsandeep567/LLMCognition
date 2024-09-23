import os
import tiktoken
from dotenv import load_dotenv
from passlib.context import CryptContext

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
    return password_context.hash(password)


# Helper function to verify passwords
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)


# Helper function to count tokens
def count_tokens(text: str) -> int:
    encoding = tiktoken.encoding_for_model("gpt-4o")
    return len(encoding.encode(text))


# Helper function to generate response restriction
def generate_restriction(final_answer: str) -> str:
    words = final_answer.split()
    if len(words) <= 10:
        return f"Restrict your response to {len(words)} words only."
    elif final_answer.replace(" ", "").isdigit():
        return "Provide only numerical values in your response."
    else:
        return ""