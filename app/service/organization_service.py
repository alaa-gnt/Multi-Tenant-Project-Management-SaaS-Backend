from sqlalchemy.orm import Session
from app.db.repository import OrganizationRepository, UserRepository
from app.db.schema import OrganizationCreate, OrganizationResponse, OrganizationUpdate
from fastapi import HTTPException, status
from app.db.models.organization import Organization
from app.db.models.user import User

# ===== Organization Setup ===== #

# --------------------------------------------------------------------------------
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
# --------------------------------------------------------------------------------


# --------------------------------------------------------------------------------
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
# --------------------------------------------------------------------------------

# ===== Invite Management ===== #


# --------------------------------------------------------------------------------
def getInviteCode(current_user: User, db: Session) -> str:
    """Get invite code for current user's organization (owner only)"""
    org_repo = OrganizationRepository(db)
    
    # Check if user has an organization
    if current_user.org_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You don't belong to any organization."
        )
    
    # Check if user is owner
    if current_user.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization owner can access the invite code."
        )
    
    # Get organization
    organization = org_repo.get_by_id(current_user.org_id)
    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found."
        )
    
    return organization.invite_code
# --------------------------------------------------------------------------------


# --------------------------------------------------------------------------------
def regenerateInviteCode(current_user: User, db: Session) -> str:
    """Regenerate invite code for current user's organization (owner only)"""
    org_repo = OrganizationRepository(db)
    
    # Check if user has an organization
    if current_user.org_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You don't belong to any organization."
        )
    
    # Check if user is owner
    if current_user.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization owner can regenerate the invite code."
        )
    
    # Regenerate invite code
    organization = org_repo.regenerate_invite_code(current_user.org_id)
    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found."
        )
    
    return organization.invite_code
# --------------------------------------------------------------------------------


# ===== Organization Info ===== #


# --------------------------------------------------------------------------------
def getOrganizationDetailes(current_user: User, db: Session) -> dict:
    """Get detailed information about current user's organization"""
    org_repo = OrganizationRepository(db)

    if current_user.org_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You don't belong to any organization."
        )
    
    # Get organization with user and project counts
    org_details = org_repo.get_with_details(current_user.org_id)
    if org_details is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found."
        )
    
    # Extract organization and counts
    organization = org_details["organization"]
    
    return {
        "id": organization.id,
        "name": organization.name,
        "description": organization.description,
        "owner_id": organization.owner_id,
        "invite_code": organization.invite_code if current_user.role == "owner" else None,
        "users_count": org_details["users_count"],
        "projects_count": org_details["projects_count"],
        "your_role": current_user.role
    }
# --------------------------------------------------------------------------------


# ===== Member Management ===== #


# --------------------------------------------------------------------------------
def updateMemberRole(target_user_id: int, new_role: str, current_user: User, db: Session) -> dict:
    """Update a member's role in the organization (owner only)"""
    org_repo = OrganizationRepository(db)
    user_repo = UserRepository(db)
    
    # Check if current user has an organization
    if current_user.org_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You don't belong to any organization."
        )
    
    # Check if current user is owner
    if current_user.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization owner can update member roles."
        )
    
    # Validate new role
    valid_roles = ["member", "admin", "owner"]
    if new_role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )
    
    # Get target user
    target_user = user_repo.get_by_id(target_user_id)
    if target_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    
    # Check if target user belongs to the same organization
    if target_user.org_id != current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not belong to your organization."
        )
    
    # Prevent changing your own role
    if target_user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot change your own role."
        )
    
    # Update role
    updated_user = user_repo.assign_to_organization(target_user_id, current_user.org_id, new_role)
    
    return {
        "user_id": updated_user.id,
        "name": updated_user.name,
        "email": updated_user.email,
        "new_role": updated_user.role
    }
# --------------------------------------------------------------------------------


# ===== Organization Settings ===== #


# --------------------------------------------------------------------------------
def updateOrganization(org_data: OrganizationUpdate, current_user: User, db: Session) -> OrganizationResponse:
    """Update organization details (owner only)"""
    org_repo = OrganizationRepository(db)
    
    # Check if user has an organization
    if current_user.org_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You don't belong to any organization."
        )
    
    # Check if user is owner
    if current_user.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization owner can update organization details."
        )
    
    # Update organization
    updated_org = org_repo.update(current_user.org_id, org_data)
    if updated_org is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found."
        )
    
    return updated_org
# --------------------------------------------------------------------------------


# --------------------------------------------------------------------------------
def deleteOrganization(current_user: User, db: Session) -> dict:
    """Delete organization and remove all members (owner only, dangerous!)"""
    org_repo = OrganizationRepository(db)
    user_repo = UserRepository(db)
    
    # Check if user has an organization
    if current_user.org_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You don't belong to any organization."
        )
    
    # Check if user is owner
    if current_user.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization owner can delete the organization."
        )
    
    org_id = current_user.org_id
    
    # Get all users in the organization
    all_users = user_repo.get_all_by_organization(org_id)
    
    # Remove all users from organization (set org_id and role to None)
    for user in all_users:
        user_repo.assign_to_organization(user.id, None, None)
    
    # Delete the organization
    success = org_repo.delete(org_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found."
        )
    
    return {
        "message": "Organization deleted successfully",
        "deleted_org_id": org_id,
        "users_affected": len(all_users)
    }
# --------------------------------------------------------------------------------


# ===== User Actions ===== #


# --------------------------------------------------------------------------------
def leaveOrganization(current_user: User, db: Session) -> dict:
    """Leave current organization (owner cannot leave if they are the only owner)"""
    org_repo = OrganizationRepository(db)
    user_repo = UserRepository(db)
    
    # Check if user has an organization
    if current_user.org_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You don't belong to any organization."
        )
    
    # Check if user is owner
    if current_user.role == "owner":
        # Count users in organization
        all_users = user_repo.get_all_by_organization(current_user.org_id)
        if len(all_users) > 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Owner cannot leave organization while other members exist. Transfer ownership or delete the organization first."
            )
        # If owner is alone, they can leave (org becomes ownerless, or you could auto-delete it)
    
    org_id = current_user.org_id
    
    # Remove user from organization
    user_repo.assign_to_organization(current_user.id, None, None)
    
    return {
        "message": "Successfully left organization",
        "previous_org_id": org_id
    }
# --------------------------------------------------------------------------------


# --------------------------------------------------------------------------------
def transferOwnership(new_owner_id: int, current_user: User, db: Session) -> dict:
    """Transfer ownership to another member in the organization"""
    org_repo = OrganizationRepository(db)
    user_repo = UserRepository(db)
    
    # Check if user has an organization
    if current_user.org_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You don't belong to any organization."
        )
    
    # Check if current user is owner
    if current_user.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization owner can transfer ownership."
        )
    
    # Get new owner
    new_owner = user_repo.get_by_id(new_owner_id)
    if new_owner is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    
    # Check if new owner belongs to the same organization
    if new_owner.org_id != current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not belong to your organization."
        )
    
    # Prevent transferring to yourself
    if new_owner_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already the owner."
        )
    
    # Update organization owner_id
    org = org_repo.get_by_id(current_user.org_id)
    org.owner_id = new_owner_id
    db.commit()
    db.refresh(org)
    
    # Update roles: new owner gets "owner", current owner becomes "member"
    user_repo.assign_to_organization(new_owner_id, current_user.org_id, "owner")
    user_repo.assign_to_organization(current_user.id, current_user.org_id, "member")
    
    return {
        "message": "Ownership transferred successfully",
        "new_owner_id": new_owner_id,
        "new_owner_name": new_owner.name,
        "previous_owner_id": current_user.id
    }
# --------------------------------------------------------------------------------