from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.core.security import require_analyst
from app.models.slick_detection import SlickDetection
from app.schemas.detection import AnalyzeRequest, DetectionResponse
from app.services.detection_service import analyze_slick
from app.services.investigation_service import to_geojson_polygon

router = APIRouter(prefix="/detections", tags=["Slick Detection"], dependencies=[Depends(require_analyst)])

@router.get("", response_model=List[DetectionResponse])
async def list_detections(db: AsyncSession = Depends(get_db)):
    """List all slick detections (protected)."""
    stmt = select(SlickDetection)
    res = await db.execute(stmt)
    detections = res.scalars().all()

    return [
        DetectionResponse(
            detection_id=d.id,
            slick_polygon=to_geojson_polygon(d.geometry),
            area_km2=d.area_km2,
            length_km=d.length_km,
            width_km=d.width_km,
            orientation_deg=d.orientation_deg,
            confidence=d.confidence,
            age_estimate_hours=d.age_estimate_hours,
            age_confidence=d.age_confidence
        ) for d in detections
    ]

@router.post("/analyze", response_model=DetectionResponse, status_code=status.HTTP_201_CREATED)
async def analyze(req: AnalyzeRequest, db: AsyncSession = Depends(get_db)):
    """Analyze a satellite scene to detect and characterize oil slicks (protected)."""
    slick = await analyze_slick(db, req)
    return DetectionResponse(
        detection_id=slick.id,
        slick_polygon=to_geojson_polygon(slick.geometry),
        area_km2=slick.area_km2,
        length_km=slick.length_km,
        width_km=slick.width_km,
        orientation_deg=slick.orientation_deg,
        confidence=slick.confidence,
        age_estimate_hours=slick.age_estimate_hours,
        age_confidence=slick.age_confidence
    )
