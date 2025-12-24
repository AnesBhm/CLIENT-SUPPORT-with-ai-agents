import bcrypt
from datetime import datetime, timedelta
from jose import jwt
from typing import Any, Union

SECRET_KEY = "CHANGE_THIS_TO_A_COMPLETE_SECRET_KEY_IN_PRODUCTION"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against the hashed version.
    """
    # bcrypt requires bytes, so we encode the strings
    password_byte_enc = plain_password.encode('utf-8')
    hashed_password_byte_enc = hashed_password.encode('utf-8')
    
    # checkpw securely checks the password
    return bcrypt.checkpw(password_byte_enc, hashed_password_byte_enc)

def get_password_hash(password: str) -> str:
    """
    Hashes a password using bcrypt with a salt.
    """
    pwd_bytes = password.encode('utf-8')
    
    # gensalt(rounds=12) generates a salt and configures the work factor.
    # rounds=12 is standard; increase to 14+ for higher security (slower).
    salt = bcrypt.gensalt(rounds=12)
    
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    
    # Return as string to be compatible with your database model
    return hashed.decode('utf-8')

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt