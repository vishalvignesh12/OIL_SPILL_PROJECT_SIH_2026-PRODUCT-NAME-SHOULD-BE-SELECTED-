from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel
from app.schemas.incident import GeoJSONPoint

class VesselResponse(BaseModel):
    id: UUID
    mmsi: str
    imo: Optional[str] = None
    name: str
    type: Optional[str] = None
    flag: Optional[str] = None
    length: Optional[float] = None

    class Config:
        from_attributes = True

class VesselTrackResponse(BaseModel):
    vessel_id: UUID
    track: List[GeoJSONPoint]
