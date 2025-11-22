from pydantic import BaseModel, Field
from uuid import UUID


class SeatBase(BaseModel):
    trip_id: UUID
    seat_number: int = Field(..., ge=1)
    price: int = Field(..., gt=0)


class SeatCreate(SeatBase):
    pass


class SeatResponse(SeatBase):
    id: UUID
    
    class Config:
        from_attributes = True

