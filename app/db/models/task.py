from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String)
    status = Column(String)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)

    # Relationships
    project = relationship("Project", back_populates="tasks")
    organization = relationship("Organization", back_populates="tasks")
