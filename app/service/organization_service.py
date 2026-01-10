from sqlalchemy.orm import Session
from app.db.repository import OrganizationRepository, UserRepository
from app.db.schema import OrganizationCreate, OrganizationResponse, OrganizationUpdate
from fastapi import HTTPException, status
from app.db.models.organization import Organization
from app.db.models.user import User


def createOrganization(org_data: OrganizationCreate, current_user: User, db: Session) -> OrganizationResponse:
    """Create a new organization and assign current user as owner"""
    org_repo = OrganizationRepository(db)
    user_repo = UserRepository(db)
    
    if current_user.org_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already belong to an organization. You cannot create another one."
        )
    
    organization = org_repo.create(org_data, owner_id=current_user.id, generate_code=True)
    
    user_repo.assign_to_organization(current_user.id, organization.id, role="owner")
    
    return organization

def joinOrganization(current_user: User, invite_code: str, db: Session) -> OrganizationResponse:
    org_repo = OrganizationRepository(db)
    user_repo = UserRepository(db)
    
    if current_user.org_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already belong to an organization. You cannot join another one."
        )
    
    org = org_repo.get_by_invite_code(invite_code)
    if org is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid invite code. Organization does not exist."
        )
    
    user_repo.assign_to_organization(current_user.id, org.id, role="member")
    
    return org
