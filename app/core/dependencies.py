from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt , JWTError
from app.core.security import SECRET_KEY, ALGORITHM
from app.db.repository.user import get_by_id
from app.core.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# a function to get the user , it takes the token and the database as paramters
def get_current_user(token : str = Depends(oauth2_scheme) , db=Depends(get_db)):
    try:
        payload = jwt.decode(token , SECRET_KEY , algorithms=ALGORITHM)
        user_id = payload.get("user_id")
        if user_id is None : 
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid toke payload"
            )
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid toke"
        )
    user = get_by_id(db , user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


def require_role(allowed_roles:list):
    def role_checker(user=Depends(get_current_user)):
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not allowed"
            )
        return user
    return role_checker