from pydantic import BaseModel, Field, validator
from typing import Optional


class SendVerificationRequest(BaseModel):
    mobile: str = Field(..., min_length=11, max_length=11)
    
    @validator('mobile')
    def validate_mobile(cls, v):
        if not v.startswith('09') or not v.isdigit():
            raise ValueError('Mobile must be Iranian format: 09xxxxxxxxx')
        return v


class VerifyCodeRequest(BaseModel):
    mobile: str = Field(..., min_length=11, max_length=11)
    code: str = Field(..., min_length=6, max_length=6)
    password: Optional[str] = Field(None, min_length=6)


class LoginRequest(BaseModel):
    mobile: str = Field(..., min_length=11, max_length=11)
    password: str = Field(..., min_length=6)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

