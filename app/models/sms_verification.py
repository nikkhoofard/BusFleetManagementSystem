from pydantic import BaseModel, Field, validator
from datetime import datetime
from uuid import UUID
from typing import Optional


class SMSVerificationBase(BaseModel):
    mobile: str = Field(..., min_length=11, max_length=11)
    code: str = Field(..., min_length=6, max_length=6)
    expires_at: datetime
    verified: bool = False


class SMSVerificationCreate(BaseModel):
    mobile: str = Field(..., min_length=11, max_length=11)
    
    @validator('mobile')
    def validate_mobile(cls, v):
        if not v.startswith('09') or not v.isdigit():
            raise ValueError('Mobile must be Iranian format: 09xxxxxxxxx')
        return v


class SMSVerificationVerify(BaseModel):
    mobile: str = Field(..., min_length=11, max_length=11)
    code: str = Field(..., min_length=6, max_length=6)
    password: Optional[str] = Field(None, min_length=6)


class SMSVerificationResponse(SMSVerificationBase):
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

