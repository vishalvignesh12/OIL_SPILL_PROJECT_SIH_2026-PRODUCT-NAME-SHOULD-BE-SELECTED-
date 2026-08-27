from datetime import datetime
from typing import Optional, List, Literal, Tuple, Union
from uuid import UUID
from pydantic import BaseModel, Field
from app.schemas.incident import GeoJSONPoint
from app.schemas.scene import GeoJSONPolygon

class GeoJSONLineString(BaseModel):
    type: Literal["LineString"] = "LineString"
    coordinates: List[Tuple[float, float]]

class HindcastRequest(BaseModel):
    incident_id: UUID
    slick_polygon: GeoJSONPolygon
    timestamp: datetime

class ForecastRequest(BaseModel):
    incident_id: UUID
    slick_polygon: GeoJSONPolygon
    timestamp: datetime

class DriftResponse(BaseModel):
    origin_point: Optional[GeoJSONPoint] = None
    origin_probability_cone: Optional[GeoJSONPolygon] = None
    origin_time_estimate: Optional[datetime] = None
    origin_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    hindcast_path: Optional[GeoJSONLineString] = None
    forward_path: Optional[GeoJSONLineString] = None

    class Config:
        from_attributes = True
