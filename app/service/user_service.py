from sqlalchemy.orm import Session
from app.db.repository import UserRepository
from app.db.schema import UserCreate, UserUpdate, UserResponse, UserLogin
from app.core.security import hash_password, verify_password, create_access_token
from fastapi import HTTPException, status
from app.db.models.user import User


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


def updateUser(data: UserUpdate, target_user_id: int, current_user: User, db: Session):
    user_repo = UserRepository(db)

    user = user_repo.get_by_id(target_user_id)

    if not user:
        raise HTTPException(404 , detail="user not found")
    
    if user.org_id != current_user.org_id:
        raise HTTPException(404 , "cant update user from diffrent  organization")
    
    if data.role is not None and current_user.role != "owner":
        raise HTTPException(403 , detail="only owners can change roles")
    
    if user.role == "owner" and data.role is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Owner role cannot be changed"
        )
    
    if data.email is not None and data.email != user.email:
        if user_repo.email_exists(data.email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Email already exists")
        
    if data.password is not None:
        data.password = hash_password(data.password)

    updated_user = user_repo.update(target_user_id, data)

    return updated_user

# ==== Get / Fetch User Functions ==== #

# ------------------------------------------------------------------------------
# get a user by its id wish a condition that its from ur same organization
def getUserById(user_id: int, current_user: User, db: Session):
    user_repo = UserRepository(db)
    
    # Get user by ID
    user = user_repo.get_by_id(user_id)
    
    # Check if user exists
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if both users are in same organization
    if user.org_id != current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access users from different organizations"
        )
    
    return user
# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Get current authenticated user's profile with organization details
def getCurrentUserProfile(current_user: User, db: Session):
    user_repo = UserRepository(db)
    
    # Fetch user with organization details
    user = user_repo.get_with_organization(current_user.id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user
# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------
# Get all users in current user's organization with pagination
def getAllUsersInOrganization(current_user: User, db: Session, skip: int = 0, limit: int = 10):
    user_repo = UserRepository(db)
    
    # Get all users from the same organization
    users = user_repo.get_all_by_organization(
        org_id=current_user.org_id,
        skip=skip,
        limit=limit
    )
    
    return users
# --------------------------------------------------------------------------------


# ==== Update Functions ==== #



# --------------------------------------------------------------------------------
def updateOwnProfile(data:UserUpdate , current_user:User , db:Session):
    user_repo = UserRepository(db)

    if data.role is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot change your own role"
        )
    
    # Users cannot change their organization
    if data.org_id is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot change your organization"
        )
    
    if data.email is not None and data.email != current_user.email:
        if user_repo.email_exists(data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        
    if data.password is not None:
        data.password = hash_password(data.password)

    updated_user = user_repo.update(current_user.id, data)

    return updated_user
# --------------------------------------------------------------------------------

    

