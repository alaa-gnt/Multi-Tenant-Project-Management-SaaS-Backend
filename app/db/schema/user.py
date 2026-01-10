from pydantic import BaseModel, EmailStr
from typing import Optional


class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: Optional[str] = None


class UserCreate(UserBase):
    password: str
    org_id: Optional[int] = None
    role: Optional[str] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None
    org_id: Optional[int] = None


class UserResponse(UserBase):
    id: int
    org_id: Optional[int] = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str
