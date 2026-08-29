from datetime import datetime
from typing import Optional, List, Literal, Tuple, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

class GeoJSONPolygon(BaseModel):
    type: Literal["Polygon"] = "Polygon"
    coordinates: List[List[Tuple[float, float]]]

class SceneBase(BaseModel):
    source: str
    scene_id: str
    satellite: str
    sensor: Optional[str] = None
    product_type: str
    polarization: Optional[str] = None
    acquisition_time: datetime
    processing_time: Optional[datetime] = None
    bbox: GeoJSONPolygon
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    scene_metadata: Optional[Dict[str, Any]] = None
    status: Optional[str] = None

class SceneCreate(SceneBase):
    pass

class SceneResponse(SceneBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
