from datetime import datetime, timedelta, UTC
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.core.security import require_analyst
from app.models.vessel import Vessel
from app.models.ais_track import AISTrack
from app.schemas.vessel import VesselResponse, VesselTrackResponse
from app.services.dashboard_service import to_geojson_point

router = APIRouter(prefix="/vessels", tags=["Vessels Explorer"], dependencies=[Depends(require_analyst)])

@router.get("", response_model=List[VesselResponse])
async def list_vessels(db: AsyncSession = Depends(get_db)):
    """List all registered vessels in the system (protected)."""
    stmt = select(Vessel)
    res = await db.execute(stmt)
    vessels = res.scalars().all()
    
    return [
        VesselResponse(
            id=v.id,
            mmsi=v.mmsi,
            imo=v.imo,
            name=v.name,
            type=v.type,
            flag=v.flag,
            length=v.length
        ) for v in vessels
    ]

@router.get("/{id}", response_model=VesselResponse)
async def get_vessel(id: UUID, db: AsyncSession = Depends(get_db)):
    """Retrieve details for a specific vessel (protected)."""
    stmt = select(Vessel).where(Vessel.id == id)
    res = await db.execute(stmt)
    v = res.scalars().first()
    if not v:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vessel not found")
        
    return VesselResponse(
        id=v.id,
        mmsi=v.mmsi,
        imo=v.imo,
        name=v.name,
        type=v.type,
        flag=v.flag,
        length=v.length
    )

@router.get("/{id}/track", response_model=VesselTrackResponse)
async def get_vessel_track(id: UUID, db: AsyncSession = Depends(get_db)):
    """Retrieve historical AIS tracks for a specific vessel (protected)."""
    stmt = select(AISTrack).where(AISTrack.vessel_id == id).order_by(AISTrack.timestamp.asc())
    res = await db.execute(stmt)
    pts = res.scalars().all()
    
    geojson_pts = [to_geojson_point(pt.position) for pt in pts]
    
    return VesselTrackResponse(
        vessel_id=id,
        track=geojson_pts
    )
