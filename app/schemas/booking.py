from pydantic import BaseModel, Field, validator
from datetime import datetime
from uuid import UUID
from typing import Optional, List


class ReserveSeatRequest(BaseModel):
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


class ReserveSeatResponse(BaseModel):
    reservation_id: UUID
    expires_at: datetime
    payment_deadline: datetime


class PayBookingRequest(BaseModel):
    reservation_id: UUID


class BookingResponse(BaseModel):
    id: UUID
    user_id: UUID
    trip_id: UUID
    seat_id: UUID
    first_name: str
    last_name: str
    national_id: str
    gender: bool
    price_paid: int
    status: str
    created_at: datetime
    cancelled_at: Optional[datetime] = None


class ReservationResponse(BaseModel):
    id: UUID
    user_id: UUID
    seat_id: UUID
    trip_id: UUID
    expires_at: datetime
    status: str
    created_at: datetime


class AvailableTripResponse(BaseModel):
    trip_id: UUID
    bus_id: UUID
    plate_number: str
    departure_time: datetime
    arrival_time: datetime
    origin: str
    destination: str
    available_seats: List[dict]  # List of {seat_id, seat_number, price}


class AvailableTripsQuery(BaseModel):
    origin: Optional[str] = None
    destination: Optional[str] = None
    sort_by: Optional[str] = Field(None, pattern="^(price_asc|price_desc)$")

