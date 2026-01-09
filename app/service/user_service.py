from sqlalchemy.orm import Session
from app.db.repository import UserRepository
from app.db.schema import UserCreate, UserUpdate, UserResponse, UserLogin
from app.core.security import hash_password, verify_password, create_access_token
from fastapi import HTTPException, status


def userRegistration(data: UserCreate, db: Session) -> UserResponse:
    user_repo = UserRepository(db)
    
    if user_repo.email_exists(data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    
    hashed_password = hash_password(data.password)
    data.password = hashed_password
    user = user_repo.create(data)
    
    return user

def userLogin(data: UserLogin, db: Session):
    user_repo = UserRepository(db)

    # Get user by email
    user = user_repo.get_by_email(data.email)
    
    # Check if user exists
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create access token
    token_data = {
        "user_id": user.id,
        "email": user.email,
        "org_id": user.org_id
    }
    access_token = create_access_token(token_data)
    
    # Return token and user info (without password)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "org_id": user.org_id
        }
    }
    
