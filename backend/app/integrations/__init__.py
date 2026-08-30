from app.integrations.satellite import SatelliteAdapterProtocol, FixtureSatelliteAdapter
from app.integrations.opendrift import DriftAdapterProtocol, FixtureDriftAdapter
from app.integrations.global_fishing_watch import AISAdapterProtocol, FixtureAISAdapter
from app.integrations.weather import WeatherAdapterProtocol, FixtureWeatherAdapter

__all__ = [
    "SatelliteAdapterProtocol", "FixtureSatelliteAdapter",
    "DriftAdapterProtocol", "FixtureDriftAdapter",
    "AISAdapterProtocol", "FixtureAISAdapter",
    "WeatherAdapterProtocol", "FixtureWeatherAdapter"
]
