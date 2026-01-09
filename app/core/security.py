from passlib.context import CryptContext
from jose import jwt
from datetime import datetime , timedelta

# this function manage the hashing algorithms 
pwd_context = CryptContext(schemes=["bcrypt"] , deprecated="auto")

# helper functions
def hash_password(password : str) -> str:
    return pwd_context.hash(password)

def verfy_password(plain_password : str , hash_password:str) -> bool:
    return pwd_context.verify(plain_password , hash_password)

SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# main function of the JWT token 

def create_access_token(data : dict):
    to_encode = data.copy()
    experation = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp' : experation})
    return jwt.encode(to_encode , SECRET_KEY , algorithm=ALGORITHM)

