from datetime import datetime
from typing import Optional, List, Literal, Tuple, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.incident import GeoJSONPoint
from app.schemas.scene import GeoJSONPolygon


class GeoJSONCentroid(BaseModel):
    """GeoJSON Point for centroid coordinates."""
    type: Literal["Point"] = "Point"
    coordinates: Tuple[float, float]  # [longitude, latitude]


class GeoJSONBBox(BaseModel):
    """GeoJSON Bounding Box."""
    type: Literal["Polygon"] = "Polygon"
    coordinates: List[List[Tuple[float, float]]]  # [[[min_lon, min_lat], [max_lon, min_lat], [max_lon, max_lat], [min_lon, max_lat], [min_lon, min_lat]]]


class SpillRegionResponse(BaseModel):
    """Response model for a spill region."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    confidence: float = Field(..., ge=0.0, le=1.0)
    area_m2: float = Field(..., ge=0.0)
    # Note: Perimeter is optional in PRD
    perimeter_m: Optional[float] = Field(None, ge=0.0)
    # Centroid as lat/lon object (not GeoJSON for simplicity in API)
    centroid: Dict[str, float] = Field(..., example={"lat": 12.231, "lon": 68.231})
    # Bounding box as lat/lng object
    bbox: Dict[str, float] = Field(..., example={
        "min_lat": 12.20,
        "min_lon": 68.20,
        "max_lat": 12.27,
        "max_lon": 68.27
    })
    # Geometry as GeoJSON
    geometry: GeoJSONPolygon
    # Optional fields from PRD
    mask_uri: Optional[str] = None
    created_at: Optional[datetime] = None