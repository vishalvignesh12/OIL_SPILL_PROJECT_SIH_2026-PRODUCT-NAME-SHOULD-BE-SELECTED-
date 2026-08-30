import uuid
from datetime import datetime, UTC
from typing import Dict, Any, Protocol
from app.schemas.scene import GeoJSONPolygon

class SatelliteAdapterProtocol(Protocol):
    async def analyze_scene(self, scene_id: str, image_url: str, timestamp: datetime) -> Dict[str, Any]:
        ...

class FixtureSatelliteAdapter:
    """Fixture satellite adapter returning realistic mock slick detection data."""
    async def analyze_scene(self, scene_id: str, image_url: str, timestamp: datetime) -> Dict[str, Any]:
        # Return a deterministic mock response based on the scene_id
        # We define a mock geometry that represents a typical slick near the coast
        mock_polygon = {
            "type": "Polygon",
            "coordinates": [[
                [76.10, 9.80],
                [76.12, 9.81],
                [76.15, 9.85],
                [76.13, 9.86],
                [76.09, 9.82],
                [76.10, 9.80]
            ]]
        }
        
        # Determine confidence and properties based on scene ID
        is_low_conf = "low" in scene_id.lower()
        confidence = 0.45 if is_low_conf else 0.94
        age_hours = 24.0 if is_low_conf else 18.0
        age_conf = "LOW" if is_low_conf else "HIGH"
        
        return {
            "detection_id": uuid.uuid4(),
            "slick_polygon": mock_polygon,
            "area_km2": 12.42,
            "length_km": 8.21,
            "width_km": 1.42,
            "orientation_deg": 73.0,
            "confidence": confidence,
            "age_estimate_hours": age_hours,
            "age_confidence": age_conf
        }
