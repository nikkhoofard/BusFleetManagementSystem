from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserBase(BaseModel):
    mobile: str = Field(..., min_length=11, max_length=11)
    
    @validator('mobile')
    def validate_mobile(cls, v):
        if not v.startswith('09') or not v.isdigit():
            raise ValueError('Mobile must be Iranian format: 09xxxxxxxxx')
        return v


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserProfileBase(BaseModel):
    profile_type: str = Field(..., pattern="^(passenger|operator|driver|admin)$")


class UserProfileCreate(UserProfileBase):
    user_id: UUID


class UserProfileResponse(UserProfileBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

