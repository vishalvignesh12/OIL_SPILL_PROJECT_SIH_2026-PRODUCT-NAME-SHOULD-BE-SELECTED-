from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.core.security import require_admin
from app.models.user import User
from app.models.vessel import Vessel
from app.models.incident import Incident
from app.schemas.auth import UserResponse
from app.schemas.vessel import VesselResponse
from app.schemas.incident import IncidentResponse
from app.services.dashboard_service import to_geojson_point

router = APIRouter(prefix="/admin", tags=["Admin Portal"], dependencies=[Depends(require_admin)])

@router.get("/users", response_model=List[UserResponse])
async def list_users(db: AsyncSession = Depends(get_db)):
    """Retrieve list of registered users (admin-only)."""
    stmt = select(User)
    res = await db.execute(stmt)
    users = res.scalars().all()
    
    return [
        UserResponse(
            id=u.id,
            name=u.name,
            email=u.email,
            role=u.role,
            created_at=u.created_at
        ) for u in users
    ]

@router.get("/vessels", response_model=List[VesselResponse])
async def list_vessels_admin(db: AsyncSession = Depends(get_db)):
    """Retrieve list of registered vessels (admin-only)."""
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

@router.get("/incidents", response_model=List[IncidentResponse])
async def list_incidents_admin(db: AsyncSession = Depends(get_db)):
    """Retrieve list of incidents (admin-only)."""
    stmt = select(Incident)
    res = await db.execute(stmt)
    incidents = res.scalars().all()
    
    return [
        IncidentResponse(
            id=inc.id,
            name=inc.name,
            description=inc.description,
            timestamp=inc.timestamp,
            location=to_geojson_point(inc.location),
            status=inc.status,
            created_at=inc.created_at,
            updated_at=inc.updated_at
        ) for inc in incidents
    ]
