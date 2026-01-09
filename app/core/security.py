from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone
import os

# this function manage the hashing algorithms 
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# helper functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Get from environment variables (fallback for development only)
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# main function of the JWT token 

def create_access_token(data: dict):
    to_encode = data.copy()
    expiration = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expiration})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

