from pydantic import BaseModel
from typing import Optional


class TaskBase(BaseModel):
    title: str
    content: Optional[str] = None
    status: Optional[str] = None


class TaskCreate(TaskBase):
    project_id: int
    org_id: int


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    status: Optional[str] = None


class TaskResponse(TaskBase):
    id: int
    project_id: int
    org_id: int

    class Config:
        from_attributes = True
