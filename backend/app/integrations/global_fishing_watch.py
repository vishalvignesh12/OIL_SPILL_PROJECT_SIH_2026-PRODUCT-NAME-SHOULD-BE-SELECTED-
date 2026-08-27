import csv
from datetime import datetime, timedelta, UTC
from typing import List, Dict, Any, Protocol, Optional
from uuid import UUID

class AISAdapterProtocol(Protocol):
    async def get_vessels_in_region(
        self, start_time: datetime, end_time: datetime, bbox: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        ...
    async def get_track(
        self, vessel_mmsi: str, start_time: datetime, end_time: datetime
    ) -> List[Dict[str, Any]]:
        ...

class FixtureAISAdapter:
    """Fixture AIS adapter returning precomputed or sample track data."""
    def __init__(self):
        # Realistic local vessels
        self.mock_vessels = [
            {
                "mmsi": "232003423",
                "imo": "9123456",
                "name": "MSC ELSA III",
                "type": "Tanker",
                "flag": "Panama",
                "length": 245.0
            },
            {
                "mmsi": "311000124",
                "imo": "9345678",
                "name": "OCEAN VOYAGER",
                "type": "Cargo",
                "flag": "India",
                "length": 189.0
            },
            {
                "mmsi": "419000789",
                "imo": "9567890",
                "name": "KERALA STAR",
                "type": "Tanker",
                "flag": "Singapore",
                "length": 220.0
            }
        ]

    async def get_vessels_in_region(
        self, start_time: datetime, end_time: datetime, bbox: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        return self.mock_vessels

    async def get_track(
        self, vessel_mmsi: str, start_time: datetime, end_time: datetime
    ) -> List[Dict[str, Any]]:
        # Simulate track coordinates based on MMSI
        track = []
        
        # Centroid is (76.11, 9.82)
        # Origin point is (75.98, 9.72)
        # Vessel 1: MSC ELSA III - passes directly through the origin (very high correlation)
        if vessel_mmsi == "232003423":
            # Passes southwest to northeast directly through (75.98, 9.72)
            base_lon, base_lat = 75.80, 9.60
            for i in range(12):
                timestamp = start_time + timedelta(hours=i)
                # Linear path from (75.80, 9.60) to (76.24, 9.93)
                lon = base_lon + (i * 0.04)
                lat = base_lat + (i * 0.03)
                track.append({
                    "timestamp": timestamp,
                    "lon": lon,
                    "lat": lat,
                    "speed": 14.5,
                    "course": 53.0,
                    "heading": 53.0,
                    "source": "GFW"
                })
        # Vessel 2: OCEAN VOYAGER - passes far away (low correlation)
        elif vessel_mmsi == "311000124":
            base_lon, base_lat = 76.50, 9.50
            for i in range(12):
                timestamp = start_time + timedelta(hours=i)
                track.append({
                    "timestamp": timestamp,
                    "lon": base_lon,
                    "lat": base_lat + (i * 0.02),
                    "speed": 11.2,
                    "course": 0.0,
                    "heading": 0.0,
                    "source": "GFW"
                })
        # Vessel 3: KERALA STAR - passes close but has a major AIS GAP right during the spill window (75.95, 9.70)
        elif vessel_mmsi == "419000789":
            base_lon, base_lat = 75.82, 9.58
            for i in range(12):
                # Introduce a gap from hour 3 to hour 7 (4 hours dark period)
                if 3 <= i <= 7:
                    continue
                timestamp = start_time + timedelta(hours=i)
                lon = base_lon + (i * 0.035)
                lat = base_lat + (i * 0.028)
                track.append({
                    "timestamp": timestamp,
                    "lon": lon,
                    "lat": lat,
                    "speed": 15.0,
                    "course": 51.0,
                    "heading": 51.0,
                    "source": "GFW"
                })
        return track
