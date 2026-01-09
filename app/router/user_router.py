from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.db.schema.user import UserCreate, UserLogin, UserResponse
from app.service.user_service import userRegistration, userLogin

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)):
    return userRegistration(data=data, db=db)


@router.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):

    return userLogin(data=data, db=db)
