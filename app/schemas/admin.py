from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import List


class BusCreateRequest(BaseModel):
    plate_number: str = Field(..., min_length=1, max_length=20)
    capacity: int = Field(..., gt=0)
    route_id: UUID
    owner_id: UUID
    driver_ids: List[UUID] = Field(default_factory=list)


class TripCreateRequest(BaseModel):
    bus_id: UUID
    departure_time: datetime
    arrival_time: datetime
    status: str = Field(default="active", pattern="^(active|cancelled|completed)$")


class HourlyBookingsResponse(BaseModel):
    hour: int
    bookings_count: int


class BusRevenueResponse(BaseModel):
    bus_id: UUID
    plate_number: str
    month: int
    year: int
    bookings_count: int
    total_revenue: int


class BusiestDriverResponse(BaseModel):
    driver_id: UUID
    driver_mobile: str
    trips_count: int


class BusDriversResponse(BaseModel):
    driver_id: UUID
    mobile: str
    user_id: UUID

    class Config:
        from_attributes = True
