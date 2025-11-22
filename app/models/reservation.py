from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional


class ReservationBase(BaseModel):
    user_id: UUID
    seat_id: UUID
    trip_id: UUID
    expires_at: datetime
    status: str = Field(default="held", pattern="^(held|confirmed|cancelled|expired)$")


class ReservationCreate(BaseModel):
    trip_id: UUID
    seat_id: UUID
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    national_id: str = Field(..., min_length=10, max_length=10)
    gender: bool  # true = man, false = woman
    
    @validator('national_id')
    def validate_national_id(cls, v):
        if not v.isdigit() or len(v) != 10:
            raise ValueError('National ID must be 10 digits')
        return v


class ReservationResponse(ReservationBase):
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

