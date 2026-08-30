from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.incident import GeoJSONPoint
from app.schemas.scene import GeoJSONPolygon
from app.schemas.drift import GeoJSONLineString


class DashboardOverviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_incidents: int = Field(..., ge=0)
    active_incidents: int = Field(..., ge=0)
    detected_spills: int = Field(..., ge=0)
    total_spill_area_km2: float = Field(..., ge=0)
    analyses_completed: int = Field(..., ge=0)
    analyses_processing: int = Field(..., ge=0)
    analyses_failed: int = Field(..., ge=0)
    high_confidence_spills: int = Field(..., ge=0)


class IncidentItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    incident_id: UUID
    status: str
    detected_at: str  # ISO format string
    confidence: float = Field(..., ge=0.0, le=1.0)
    area_km2: float = Field(..., ge=0)
    location: GeoJSONPoint


class DashboardIncidentsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: List[IncidentItemResponse]
    page: int = Field(..., ge=1)
    page_size: int = Field(..., ge=1, le=100)
    total: int = Field(..., ge=0)


class SpillRegionProperties(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    incident_id: UUID
    detection_id: UUID
    confidence: float = Field(..., ge=0.0, le=1.0)
    area_km2: float = Field(..., ge=0)
    status: str


class DashboardSpillsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    type: str = "FeatureCollection"
    features: List[dict]  # GeoJSON Feature objects


class VesselCandidateItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    vessel_id: UUID
    name: str
    rank: int = Field(..., ge=1)
    attribution_score: float = Field(..., ge=0.0, le=1.0)
    confidence: str  # HIGH, MEDIUM, LOW based on score
    distance_to_origin_km: float = Field(..., ge=0)
    temporal_match: float = Field(..., ge=0.0, le=1.0)


class DashboardVesselsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: List[VesselCandidateItemResponse]
    page: int = Field(..., ge=1)
    page_size: int = Field(..., ge=1, le=100)
    total: int = Field(..., ge=0)


class ActivityEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    event: str
    incident_id: UUID
    timestamp: str  # ISO format string


class DashboardActivityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: List[ActivityEventResponse]


class InvestigationDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    investigation: dict  # Reuse existing InvestigationResponse or create simplified version
    detection: dict      # Reuse existing DetectionResponse or create simplified version
    spill_regions: List[dict] = []  # GeoJSON Feature objects
    hindcast: dict = {}
    forecast: dict = {}
    ais_tracks: List[dict] = []
    candidate_vessels: List[dict] = []
    attribution: dict = {}
    evidence: List[dict] = []