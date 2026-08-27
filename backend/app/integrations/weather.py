from datetime import datetime
from typing import Dict, Any, Protocol

class WeatherAdapterProtocol(Protocol):
    async def get_conditions(self, lon: float, lat: float, timestamp: datetime) -> Dict[str, Any]:
        ...

class FixtureWeatherAdapter:
    """Fixture weather adapter simulating ERA5 wind and CMEMS current data."""
    async def get_conditions(self, lon: float, lat: float, timestamp: datetime) -> Dict[str, Any]:
        return {
            "wind_speed_m_s": 5.4,
            "wind_direction_deg": 225.0, # wind blowing from southwest to northeast
            "current_speed_m_s": 0.35,
            "current_direction_deg": 45.0, # current flowing northeast
            "source_wind": "ECMWF ERA5",
            "source_current": "Copernicus CMEMS"
        }
