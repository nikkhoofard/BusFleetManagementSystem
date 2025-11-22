from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional


class BookingBase(BaseModel):
    user_id: UUID
    trip_id: UUID
    seat_id: UUID
    first_name: str
    last_name: str
    national_id: str
    gender: bool  # true = man, false = woman
    price_paid: int
    status: str = Field(default="confirmed", pattern="^(confirmed|cancelled)$")


class BookingCreate(BaseModel):
    reservation_id: UUID


class BookingResponse(BookingBase):
    id: UUID
    created_at: datetime
    cancelled_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

