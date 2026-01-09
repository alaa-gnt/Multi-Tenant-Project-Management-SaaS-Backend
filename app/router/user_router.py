from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.db.schema.user import UserResponse
from app.db.models.user import User
from typing import List

router = APIRouter(prefix="/users", tags=["Users"])


# User endpoints will go here
