import csv
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import shape, Point
from app.models.ais_track import AISTrack
from app.models.vessel import Vessel
from app.integrations.global_fishing_watch import FixtureAISAdapter

async def get_or_create_vessel_by_mmsi(db: AsyncSession, mmsi: str, mock_data: dict) -> Vessel:
    """Helper to retrieve a vessel or create it if not present."""
    stmt = select(Vessel).where(Vessel.mmsi == mmsi)
    res = await db.execute(stmt)
    vessel = res.scalars().first()
    if not vessel:
        vessel = Vessel(
            mmsi=mmsi,
            imo=mock_data.get("imo", "9000000"),
            name=mock_data.get("name", f"Vessel {mmsi}"),
            type=mock_data.get("type", "Cargo"),
            flag=mock_data.get("flag", "Panama"),
            length=mock_data.get("length", 150.0)
        )
        db.add(vessel)
        await db.flush()
    return vessel

async def query_ais_tracks(
    db: AsyncSession,
    start_time: datetime,
    end_time: datetime,
    bbox: Optional[str] = None,
    vessel_id: Optional[UUID] = None
) -> List[AISTrack]:
    """Query AIS tracks from database. If empty, seeds from integration adapter."""
    # Build query
    stmt = select(AISTrack)
    if vessel_id:
        stmt = stmt.where(AISTrack.vessel_id == vessel_id)
        
    stmt = stmt.where(AISTrack.timestamp.between(start_time, end_time))
    
    # Execute
    res = await db.execute(stmt)
    tracks = list(res.scalars().all())
    
    if not tracks:
        # DB is empty, fetch from GFW/Fixture adapter and seed
        adapter = FixtureAISAdapter()
        vessels_data = await adapter.get_vessels_in_region(start_time, end_time)
        
        for mock_v in vessels_data:
            vessel = await get_or_create_vessel_by_mmsi(db, mock_v["mmsi"], mock_v)
            mock_tracks = await adapter.get_track(mock_v["mmsi"], start_time, end_time)
            
            for pt in mock_tracks:
                geom = from_shape(Point(pt["lon"], pt["lat"]), srid=4326)
                track_pt = AISTrack(
                    vessel_id=vessel.id,
                    timestamp=pt["timestamp"],
                    position=geom,
                    speed=pt["speed"],
                    course=pt["course"],
                    heading=pt["heading"],
                    source=pt["source"]
                )
                db.add(track_pt)
        await db.commit()
        
        # Query again
        stmt = select(AISTrack)
        if vessel_id:
            stmt = stmt.where(AISTrack.vessel_id == vessel_id)
        stmt = stmt.where(AISTrack.timestamp.between(start_time, end_time))
        res = await db.execute(stmt)
        tracks = list(res.scalars().all())
        
    return tracks

async def detect_ais_gaps(tracks: List[AISTrack], threshold_hours: float = 2.0) -> List[Dict[str, Any]]:
    """Detect gaps in AIS transmission based on time discontinuities."""
    if not tracks:
        return []
        
    # Sort tracks by timestamp
    sorted_tracks = sorted(tracks, key=lambda t: t.timestamp)
    gaps = []
    
    for i in range(len(sorted_tracks) - 1):
        diff = sorted_tracks[i+1].timestamp - sorted_tracks[i].timestamp
        diff_hours = diff.total_seconds() / 3600.0
        
        if diff_hours >= threshold_hours:
            # We found a gap
            priority = "HIGH" if diff_hours >= 4.0 else "MEDIUM"
            gaps.append({
                "anomaly_flag": True,
                "gap_start": sorted_tracks[i].timestamp,
                "gap_end": sorted_tracks[i+1].timestamp,
                "priority": priority,
                "explanation": f"AIS gap of {diff_hours:.2f} hours overlaps the investigation window."
            })
            
    return gaps
