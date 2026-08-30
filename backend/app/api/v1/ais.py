from datetime import datetime
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import require_analyst
from app.schemas.incident import GeoJSONPoint
from app.services.ais_service import query_ais_tracks
from app.services.dashboard_service import to_geojson_point
from pydantic import BaseModel

router = APIRouter(prefix="/ais", tags=["AIS Transmission"], dependencies=[Depends(require_analyst)])

class AISTrackResponse(BaseModel):
    id: UUID
    vessel_id: UUID
    timestamp: datetime
    position: GeoJSONPoint
    speed: Optional[float]
    course: Optional[float]
    heading: Optional[float]
    source: Optional[str]

@router.get("", response_model=List[AISTrackResponse])
async def get_ais(
    start_time: datetime = Query(...),
    end_time: datetime = Query(...),
    bbox: Optional[str] = Query(None),
    vessel_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve filtered AIS tracks based on spatial-temporal search (protected)."""
    tracks = await query_ais_tracks(db, start_time, end_time, bbox, vessel_id)
    return [
        AISTrackResponse(
            id=t.id,
            vessel_id=t.vessel_id,
            timestamp=t.timestamp,
            position=to_geojson_point(t.position),
            speed=t.speed,
            course=t.course,
            heading=t.heading,
            source=t.source
        ) for t in tracks
    ]
