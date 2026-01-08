from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    owner = relationship("User", foreign_keys=[owner_id], back_populates="owned_organizations")
    users = relationship("User", foreign_keys="User.org_id", back_populates="organization")
    projects = relationship("Project", back_populates="organization")
    tasks = relationship("Task", back_populates="organization")
