import os
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