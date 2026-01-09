from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.db.schema.user import UserResponse , UserUpdate
from app.db.models.user import User
from typing import List
from app.service.user_service import getCurrentUserProfile 

router = APIRouter(prefix="/users", tags=["Users"])


# ===== 

#-------------------------------------------------------------------
@router.get("/me" , response_model=UserResponse)
def read_own_profile(
    current_user : User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return getCurrentUserProfile(current_user=current_user, db=db)
#-------------------------------------------------------------------

#-------------------------------------------------------------------
@router.post("/me" , response_model=UserResponse)
def update_own_profile(
    data : UserUpdate , 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)  
):
    return update_own_profile(data=data , current_user=current_user , db=db)
#-------------------------------------------------------------------