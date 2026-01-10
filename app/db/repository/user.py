from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from app.db.models.user import User
from app.db.schema.user import UserCreate, UserUpdate


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user: UserCreate) -> User:
        """Create a new user (without organization initially)"""
        db_user = User(
            name=user.name,
            email=user.email,
            password=user.password,
            role=user.role,
            org_id=user.org_id
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email (for authentication)"""
        return self.db.query(User).filter(User.email == email).first()

    def get_all_by_organization(self, org_id: int, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users in an organization"""
        return self.db.query(User).filter(User.org_id == org_id).offset(skip).limit(limit).all()

    def get_with_organization(self, user_id: int) -> Optional[User]:
        """Get user with organization details"""
        return self.db.query(User).options(joinedload(User.organization)).filter(User.id == user_id).first()

    def email_exists(self, email: str) -> bool:
        """Check if email already exists"""
        return self.db.query(User).filter(User.email == email).first() is not None

    def update(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """Update user details"""
        db_user = self.get_by_id(user_id)
        if not db_user:
            return None

        update_data = user_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)

        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def delete(self, user_id: int) -> bool:
        """Delete user"""
        db_user = self.get_by_id(user_id)
        if not db_user:
            return False

        self.db.delete(db_user)
        self.db.commit()
        return True

    def check_user_in_organization(self, user_id: int, org_id: int) -> bool:
        """Check if user belongs to organization"""
        user = self.db.query(User).filter(User.id == user_id, User.org_id == org_id).first()
        return user is not None

    def assign_to_organization(self, user_id: int, org_id: int, role: str) -> Optional[User]:
        """Assign user to an organization with a role"""
        db_user = self.get_by_id(user_id)
        if not db_user:
            return None
        
        db_user.org_id = org_id
        db_user.role = role
        
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
