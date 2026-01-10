from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.db.models.user import User
from app.db.schema import OrganizationCreate, OrganizationResponse
from app.service import organization_service
from pydantic import BaseModel


router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"]
)


class JoinOrganizationRequest(BaseModel):
    invite_code: str


@router.post("/create", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
def create_organization(
    data: OrganizationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new organization and become the owner.
    User must not already belong to an organization.
    """
    return organization_service.createOrganization(data, current_user, db)


@router.post("/join", response_model=OrganizationResponse)
def join_organization(
    data: JoinOrganizationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Join an existing organization using an invite code.
    User must not already belong to an organization.
    """
    return organization_service.joinOrganization(data.invite_code, current_user, db)


@router.get("/invite-code")
def get_invite_code(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the invite code for your organization.
    Only organization owners can access this.
    """
    return organization_service.getInviteCode(current_user, db)


@router.post("/invite-code/regenerate")
def regenerate_invite_code(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Regenerate the invite code for your organization.
    Only organization owners can do this.
    """
    return organization_service.regenerateInviteCode(current_user, db)
