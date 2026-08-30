from datetime import datetime
from typing import Optional, List, Literal, Tuple
from uuid import UUID
from pydantic import BaseModel, Field

class GeoJSONPoint(BaseModel):
    type: Literal["Point"] = "Point"
    coordinates: Tuple[float, float] # [longitude, latitude]

class IncidentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    timestamp: datetime
    location: GeoJSONPoint
    status: str = "DETECTED"

class IncidentResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    timestamp: datetime
    location: GeoJSONPoint
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
