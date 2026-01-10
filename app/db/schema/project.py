from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    deadline: Optional[datetime] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_archived: Optional[bool] = None
    deadline: Optional[datetime] = None


class ProjectResponse(ProjectBase):
    id: int
    org_id: int
    is_archived: bool
    deadline: Optional[datetime] = None

    class Config:
        from_attributes = True
