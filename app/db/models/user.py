from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    role = Column(String)
    org_id = Column(Integer, ForeignKey("organizations.id"))

    # Relationships
    organization = relationship("Organization", foreign_keys=[org_id], back_populates="users")
    owned_organizations = relationship("Organization", foreign_keys="Organization.owner_id", back_populates="owner")
