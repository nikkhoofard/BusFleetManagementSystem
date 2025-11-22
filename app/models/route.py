from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from typing import Optional


class RouteBase(BaseModel):
    origin: str = Field(..., min_length=1, max_length=100)
    destination: str = Field(..., min_length=1, max_length=100)
    distance_km: int = Field(..., gt=0)


class RouteCreate(RouteBase):
    pass


class RouteResponse(RouteBase):
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

