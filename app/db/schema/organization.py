from pydantic import BaseModel
from typing import Optional


class OrganizationBase(BaseModel):
    name: str
    description: Optional[str] = None


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    owner_id: Optional[int] = None


class OrganizationResponse(OrganizationBase):
    id: int
    owner_id: int
    invite_code: Optional[str] = None

    class Config:
        from_attributes = True


class JoinOrganizationRequest(BaseModel):
    invite_code: str


class UpdateMemberRoleRequest(BaseModel):
    user_id: int
    new_role: str


class TransferOwnershipRequest(BaseModel):
    new_owner_id: int
