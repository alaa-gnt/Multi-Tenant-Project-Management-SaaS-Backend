from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.db.models.user import User
from app.db.schema import OrganizationCreate, OrganizationResponse, OrganizationUpdate, JoinOrganizationRequest, UpdateMemberRoleRequest, TransferOwnershipRequest
from app.service import organization_service


router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"]
)


# ===== Organization Setup ===== #

@router.post("/create", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
def create_organization(
    data: OrganizationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new organization and become the owner"""
    return organization_service.createOrganization(data, current_user, db)


@router.post("/join", response_model=OrganizationResponse)
def join_organization(
    data: JoinOrganizationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Join an existing organization using an invite code"""
    return organization_service.joinOrganization(current_user, data.invite_code, db)


# ===== Invite Management ===== #

@router.get("/invite-code", response_model=str)
def get_invite_code(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the invite code for your organization (owner only)"""
    return organization_service.getInviteCode(current_user, db)


@router.post("/invite-code/regenerate", response_model=str)
def regenerate_invite_code(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Regenerate the invite code for your organization (owner only)"""
    return organization_service.regenerateInviteCode(current_user, db)


# ===== Organization Info ===== #

@router.get("/details")
def get_organization_details(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about your organization"""
    return organization_service.getOrganizationDetailes(current_user, db)


# ===== Member Management ===== #

@router.put("/members/role")
def update_member_role(
    data: UpdateMemberRoleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a member's role in the organization (owner only)"""
    return organization_service.updateMemberRole(data.user_id, data.new_role, current_user, db)


# ===== Organization Settings ===== #

@router.put("/update", response_model=OrganizationResponse)
def update_organization(
    data: OrganizationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update organization name and description (owner only)"""
    return organization_service.updateOrganization(data, current_user, db)


@router.delete("/delete")
def delete_organization(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete the organization and remove all members (owner only)"""
    return organization_service.deleteOrganization(current_user, db)


# ===== User Actions ===== #

@router.post("/leave")
def leave_organization(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Leave your current organization"""
    return organization_service.leaveOrganization(current_user, db)


@router.post("/transfer-ownership")
def transfer_ownership(
    data: TransferOwnershipRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Transfer ownership of the organization to another member (owner only)"""
    return organization_service.transferOwnership(data.new_owner_id, current_user, db)



