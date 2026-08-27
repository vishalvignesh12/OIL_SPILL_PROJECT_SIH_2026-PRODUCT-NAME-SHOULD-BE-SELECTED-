from datetime import datetime
from typing import List
from uuid import UUID
from pydantic import BaseModel, Field
from app.schemas.incident import GeoJSONPoint

class ScoreRequest(BaseModel):
    incident_id: UUID
    origin_point: GeoJSONPoint
    origin_time_start: datetime
    origin_time_end: datetime

class VesselCandidateResponse(BaseModel):
    vessel_id: UUID
    mmsi: str
    name: str
    score: float = Field(..., ge=0.0, le=1.0)
    proximity: float = Field(..., ge=0.0, le=1.0)
    temporality: float = Field(..., ge=0.0, le=1.0)
    trajectory_parity: float = Field(..., ge=0.0, le=1.0)
    anomaly_score: float = Field(..., ge=0.0, le=1.0)
    anomaly_flag: bool

class AttributionResponse(BaseModel):
    ranked_vessels: List[VesselCandidateResponse]
