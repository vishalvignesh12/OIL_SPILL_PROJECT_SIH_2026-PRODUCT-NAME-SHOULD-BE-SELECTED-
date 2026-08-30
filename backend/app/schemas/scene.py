from datetime import datetime
from typing import Optional, List, Literal, Tuple
from uuid import UUID
from pydantic import BaseModel

class GeoJSONPolygon(BaseModel):
    type: Literal["Polygon"] = "Polygon"
    coordinates: List[List[Tuple[float, float]]]

class SceneCreate(BaseModel):
    satellite: str
    product_type: str
    polarization: str
    timestamp: datetime
    bbox: GeoJSONPolygon
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None

class SceneResponse(BaseModel):
    id: UUID
    satellite: str
    product_type: str
    polarization: str
    timestamp: datetime
    bbox: GeoJSONPolygon
    image_url: Optional[str]
    thumbnail_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
