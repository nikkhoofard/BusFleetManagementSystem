from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import List, Optional


class BusBase(BaseModel):
    plate_number: str = Field(..., min_length=1, max_length=20)
    capacity: int = Field(..., gt=0)
    route_id: UUID
    owner_id: UUID


class BusCreate(BusBase):
    driver_ids: List[UUID] = Field(default_factory=list)


class BusResponse(BusBase):
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class BusDriverBase(BaseModel):
    bus_id: UUID
    driver_id: UUID
    is_active: bool = True


class BusDriverResponse(BusDriverBase):
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

