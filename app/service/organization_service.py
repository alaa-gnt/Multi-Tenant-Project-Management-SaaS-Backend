from sqlalchemy.orm import Session
from app.db.repository import OrganizationRepository, UserRepository
from app.db.schema import OrganizationCreate, OrganizationResponse, OrganizationUpdate
from fastapi import HTTPException, status
from app.db.models.organization import Organization
from app.db.models.user import User


# Organization service functions will be implemented here

