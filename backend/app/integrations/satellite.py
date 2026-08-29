import uuid
from datetime import datetime, UTC
from typing import Dict, Any, Protocol
from app.schemas.scene import GeoJSONPolygon

class SatelliteAdapterProtocol(Protocol):
    async def analyze_scene(self, scene_id: str, image_url: str, timestamp: datetime) -> Dict[str, Any]:
        ...

class FixtureSatelliteAdapter:
    """Fixture satellite adapter returning realistic mock slick detection data in PRD format."""
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

        # Generate a mock analysis ID based on scene_id
        analysis_id = f"ANL_{hash(scene_id) % 10000:04d}"

        # Determine length, width, orientation based on scene ID (for consistency with tests)
        is_low_conf = "low" in scene_id.lower()
        length_km = 8.21 if not is_low_conf else 4.10
        width_km = 1.42 if not is_low_conf else 0.71
        orientation_deg = 73.0 if not is_low_conf else 45.0

        # Return PRD-compliant format
        return {
            "analysis_id": analysis_id,
            "scene_id": scene_id,
            "status": "COMPLETED",
            "oil_spill_detected": True,
            "confidence": confidence,
            "model_version": "fixture-v1",
            "processing_time_ms": 100,  # Mock processing time
            "source_scene_id": scene_id,
            "length_km": length_km,
            "width_km": width_km,
            "orientation_deg": orientation_deg,
            "age_estimate_hours": age_hours,
            "age_confidence": age_conf,
            "spill_regions": [
                {
                    "region_id": f"region_{uuid.uuid4().hex[:8]}",
                    "confidence": confidence,
                    "area_m2": 12420000.0,  # Convert area_km2 to m2 (12.42 km2 = 12,420,000 m2)
                    "centroid": {
                        "lat": 9.828,  # Approximate centroid of the mock polygon
                        "lon": 76.118
                    },
                    "geometry": mock_polygon,
                    "bbox": {
                        "min_lat": 9.80,
                        "min_lon": 76.09,
                        "max_lat": 9.86,
                        "max_lon": 76.15
                    },
                    "mask_uri": f"storage://predictions/{scene_id}_mask.png",
                    "prediction_uri": f"storage://predictions/{scene_id}_prediction.geojson"
                }
            ]
        }
