from pydantic import BaseModel
from typing import Optional


class OrganizationBase(BaseModel):
    name: str
    description: Optional[str] = None


class OrganizationCreate(OrganizationBase):
    owner_id: int


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    owner_id: Optional[int] = None


class OrganizationResponse(OrganizationBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True
