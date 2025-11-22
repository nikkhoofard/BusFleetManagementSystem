from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional


class TripBase(BaseModel):
    bus_id: UUID
    departure_time: datetime
    arrival_time: datetime
    status: str = Field(default="active", pattern="^(active|cancelled|completed)$")


class TripCreate(TripBase):
    pass


class TripResponse(TripBase):
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

