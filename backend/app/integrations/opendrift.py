from datetime import datetime, timedelta, UTC
from typing import Dict, Any, Protocol
from app.schemas.scene import GeoJSONPolygon

class DriftAdapterProtocol(Protocol):
    async def run_hindcast(self, incident_id: str, slick_polygon: Dict[str, Any], timestamp: datetime) -> Dict[str, Any]:
        ...
    async def run_forecast(self, incident_id: str, slick_polygon: Dict[str, Any], timestamp: datetime) -> Dict[str, Any]:
        ...

class FixtureDriftAdapter:
    """Fixture drift adapter simulating particle drift backward and forward in time."""
    async def run_hindcast(self, incident_id: str, slick_polygon: Dict[str, Any], timestamp: datetime) -> Dict[str, Any]:
        # Centroid of mock slick is around (76.11, 9.82)
        # We simulate a wind/current that pushes northeast, meaning it originated southwest: (75.98, 9.72)
        origin_lon, origin_lat = 75.98, 9.72
        
        origin_pt = {
            "type": "Point",
            "coordinates": [origin_lon, origin_lat]
        }
        
        # Origin probability cone
        probability_cone = {
            "type": "Polygon",
            "coordinates": [[
                [origin_lon - 0.05, origin_lat - 0.05],
                [origin_lon + 0.05, origin_lat - 0.05],
                [origin_lon + 0.08, origin_lat + 0.05],
                [origin_lon - 0.08, origin_lat + 0.05],
                [origin_lon - 0.05, origin_lat - 0.05]
            ]]
        }
        
        # Hindcast path from origin to current position
        hindcast_path = {
            "type": "LineString",
            "coordinates": [
                [origin_lon, origin_lat],
                [origin_lon + 0.04, origin_lat + 0.03],
                [origin_lon + 0.08, origin_lat + 0.07],
                [76.11, 9.82]
            ]
        }
        
        return {
            "origin_point": origin_pt,
            "origin_probability_cone": probability_cone,
            "origin_time_estimate": timestamp - timedelta(hours=18),
            "origin_confidence": 0.72,
            "hindcast_path": hindcast_path,
            "forward_path": None
        }

    async def run_forecast(self, incident_id: str, slick_polygon: Dict[str, Any], timestamp: datetime) -> Dict[str, Any]:
        # Current centroid is (76.11, 9.82), we forecast drift northeast up to (76.25, 9.95)
        forward_path = {
            "type": "LineString",
            "coordinates": [
                [76.11, 9.82],
                [76.16, 9.86],
                [76.21, 9.91],
                [76.25, 9.95]
            ]
        }
        
        return {
            "origin_point": None,
            "origin_probability_cone": None,
            "origin_time_estimate": None,
            "origin_confidence": None,
            "hindcast_path": None,
            "forward_path": forward_path
        }
