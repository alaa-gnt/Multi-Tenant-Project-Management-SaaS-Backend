from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.db.schema.user import UserResponse , UserUpdate
from app.db.models.user import User
from typing import List
from app.service.user_service import getCurrentUserProfile , getAllUsersInOrganization , getUserById , updateUser,deleteUser,updateOwnProfile

router = APIRouter(prefix="/users", tags=["Users"])



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
    return updateOwnProfile(data=data , current_user=current_user , db=db)
#-------------------------------------------------------------------




#-------------------------------------------------------------------
@router.get("/" , response_model=List[UserResponse])
def lis_org_users(
    skip:int = 0 , 
    limit:int = 10 ,
    current_user:User = Depends(get_current_user),
    db : Session = Depends(get_db)
):
    return getAllUsersInOrganization(current_user=current_user, db=db, skip=skip, limit=limit)
#-------------------------------------------------------------------

#-------------------------------------------------------------------
@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return getUserById(user_id=user_id, current_user=current_user, db=db)
#-------------------------------------------------------------------


#-------------------------------------------------------------------
# Update another user (admin/owner)
@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return updateUser(data=data, target_user_id=user_id, current_user=current_user, db=db)
#-------------------------------------------------------------------

#-------------------------------------------------------------------
# Delete a user (owner only)
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    deleteUser(target_user_id=user_id, current_user=current_user, db=db)
    return {"detail": "User deleted successfully"}
#-------------------------------------------------------------------