from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import Optional, List
import secrets
import string
from app.db.models.organization import Organization
from app.db.models.user import User
from app.db.models.project import Project
from app.db.schema.organization import OrganizationCreate, OrganizationUpdate


class OrganizationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, organization: OrganizationCreate, owner_id: int, generate_code: bool = True) -> Organization:
        """Create a new organization with optional invite code"""
        invite_code = None
        if generate_code:
            invite_code = self._generate_unique_invite_code()
        
        db_organization = Organization(
            name=organization.name,
            description=organization.description,
            owner_id=owner_id,
            invite_code=invite_code
        )
        self.db.add(db_organization)
        self.db.commit()
        self.db.refresh(db_organization)
        return db_organization

    def get_by_id(self, org_id: int) -> Optional[Organization]:
        """Get organization by ID"""
        return self.db.query(Organization).filter(Organization.id == org_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Organization]:
        """Get all organizations"""
        return self.db.query(Organization).offset(skip).limit(limit).all()

    def get_by_owner(self, owner_id: int) -> List[Organization]:
        """Get all organizations owned by a user"""
        return self.db.query(Organization).filter(Organization.owner_id == owner_id).all()

    def get_with_details(self, org_id: int) -> Optional[dict]:
        """Get organization with users and projects count"""
        org = self.db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            return None

        users_count = self.db.query(func.count(User.id)).filter(User.org_id == org_id).scalar()
        projects_count = self.db.query(func.count(Project.id)).filter(Project.org_id == org_id).scalar()

        return {
            "organization": org,
            "users_count": users_count,
            "projects_count": projects_count
        }

    def get_with_users(self, org_id: int) -> Optional[Organization]:
        """Get organization with all users"""
        return self.db.query(Organization).options(joinedload(Organization.users)).filter(Organization.id == org_id).first()

    def get_with_projects(self, org_id: int) -> Optional[Organization]:
        """Get organization with all projects"""
        return self.db.query(Organization).options(joinedload(Organization.projects)).filter(Organization.id == org_id).first()

    def update(self, org_id: int, organization_update: OrganizationUpdate) -> Optional[Organization]:
        """Update organization details"""
        db_organization = self.get_by_id(org_id)
        if not db_organization:
            return None

        update_data = organization_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_organization, field, value)

        self.db.commit()
        self.db.refresh(db_organization)
        return db_organization

    def delete(self, org_id: int) -> bool:
        """Delete organization"""
        db_organization = self.get_by_id(org_id)
        if not db_organization:
            return False

        self.db.delete(db_organization)
        self.db.commit()
        return True

    def user_belongs_to_org(self, user_id: int, org_id: int) -> bool:
        """Check if user belongs to organization (authorization helper)"""
        user = self.db.query(User).filter(User.id == user_id, User.org_id == org_id).first()
        return user is not None

    def is_owner(self, user_id: int, org_id: int) -> bool:
        """Check if user is the owner of the organization"""
        org = self.db.query(Organization).filter(Organization.id == org_id, Organization.owner_id == user_id).first()
        return org is not None

    def get_by_invite_code(self, invite_code: str) -> Optional[Organization]:
        """Get organization by invite code"""
        return self.db.query(Organization).filter(Organization.invite_code == invite_code).first()

    def regenerate_invite_code(self, org_id: int) -> Optional[Organization]:
        """Regenerate invite code for an organization"""
        db_organization = self.get_by_id(org_id)
        if not db_organization:
            return None
        
        db_organization.invite_code = self._generate_unique_invite_code()
        self.db.commit()
        self.db.refresh(db_organization)
        return db_organization

    def _generate_unique_invite_code(self) -> str:
        """Generate a unique invite code"""
        while True:
            # Generate a code like: ABC-DEF-123
            part1 = ''.join(secrets.choice(string.ascii_uppercase) for _ in range(3))
            part2 = ''.join(secrets.choice(string.ascii_uppercase) for _ in range(3))
            part3 = ''.join(secrets.choice(string.digits) for _ in range(3))
            code = f"{part1}-{part2}-{part3}"
            
            # Check if code already exists
            existing = self.db.query(Organization).filter(Organization.invite_code == code).first()
            if not existing:
                return code
