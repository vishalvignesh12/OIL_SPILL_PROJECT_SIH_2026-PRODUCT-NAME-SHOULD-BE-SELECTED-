from datetime import datetime
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import shape
from app.core.database import get_db
from app.core.security import require_analyst
from app.models.satellite_scene import SatelliteScene
from app.schemas.scene import SceneCreate, SceneResponse
from app.services.investigation_service import to_geojson_polygon

router = APIRouter(prefix="/scenes", tags=["Satellite Scenes"], dependencies=[Depends(require_analyst)])

@router.get("", response_model=List[SceneResponse])
async def list_scenes(db: AsyncSession = Depends(get_db)):
    """List all registered satellite scenes (protected)."""
    stmt = select(SatelliteScene)
    res = await db.execute(stmt)
    scenes = res.scalars().all()
    
    return [
        SceneResponse(
            id=s.id,
            satellite=s.satellite,
            product_type=s.product_type,
            polarization=s.polarization,
            timestamp=s.timestamp,
            bbox=to_geojson_polygon(s.bbox),
            image_url=s.image_url,
            thumbnail_url=s.thumbnail_url,
            created_at=s.created_at
        ) for s in scenes
    ]

@router.get("/{id}", response_model=SceneResponse)
async def get_scene(id: UUID, db: AsyncSession = Depends(get_db)):
    """Retrieve details for a specific satellite scene (protected)."""
    stmt = select(SatelliteScene).where(SatelliteScene.id == id)
    res = await db.execute(stmt)
    s = res.scalars().first()
    if not s:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Satellite scene not found")
        
    return SceneResponse(
        id=s.id,
        satellite=s.satellite,
        product_type=s.product_type,
        polarization=s.polarization,
        timestamp=s.timestamp,
        bbox=to_geojson_polygon(s.bbox),
        image_url=s.image_url,
        thumbnail_url=s.thumbnail_url,
        created_at=s.created_at
    )

@router.post("", response_model=SceneResponse, status_code=status.HTTP_201_CREATED)
async def create_scene(req: SceneCreate, db: AsyncSession = Depends(get_db)):
    """Register metadata for a new satellite scene (protected)."""
    geom = from_shape(shape(req.bbox.model_dump()), srid=4326)
    
    s = SatelliteScene(
        satellite=req.satellite,
        product_type=req.product_type,
        polarization=req.polarization,
        timestamp=req.timestamp,
        bbox=geom,
        image_url=req.image_url,
        thumbnail_url=req.thumbnail_url
    )
    db.add(s)
    await db.commit()
    await db.refresh(s)
    
    return SceneResponse(
        id=s.id,
        satellite=s.satellite,
        product_type=s.product_type,
        polarization=s.polarization,
        timestamp=s.timestamp,
        bbox=to_geojson_polygon(s.bbox),
        image_url=s.image_url,
        thumbnail_url=s.thumbnail_url,
        created_at=s.created_at
    )
