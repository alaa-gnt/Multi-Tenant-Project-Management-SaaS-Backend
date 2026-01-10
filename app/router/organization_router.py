from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.db.models.user import User
from app.db.schema import OrganizationCreate, OrganizationResponse
from app.service import organization_service


router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"]
)


