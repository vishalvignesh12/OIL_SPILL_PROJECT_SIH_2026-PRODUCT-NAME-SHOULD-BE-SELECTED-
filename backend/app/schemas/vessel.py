from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from app.schemas.incident import GeoJSONPoint

class VesselResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    mmsi: str
    imo: Optional[str] = None
    name: str
    type: Optional[str] = None
    flag: Optional[str] = None
    length: Optional[float] = None

class VesselTrackResponse(BaseModel):
    vessel_id: UUID
    track: List[GeoJSONPoint]
