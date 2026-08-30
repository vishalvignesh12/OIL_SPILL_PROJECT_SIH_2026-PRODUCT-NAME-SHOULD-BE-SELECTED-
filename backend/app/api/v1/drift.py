from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import require_analyst
from app.schemas.drift import HindcastRequest, ForecastRequest, DriftResponse
from app.services.drift_service import calculate_hindcast, calculate_forecast
from app.services.investigation_service import to_geojson_point, to_geojson_polygon, to_geojson_linestring

router = APIRouter(prefix="/drift", tags=["Drift Analysis"], dependencies=[Depends(require_analyst)])

@router.post("/hindcast", response_model=DriftResponse, status_code=status.HTTP_201_CREATED)
async def hindcast(req: HindcastRequest, db: AsyncSession = Depends(get_db)):
    """Perform drift hindcast to estimate spill origin point/time window (protected)."""
    drift = await calculate_hindcast(db, req)
    return DriftResponse(
        origin_point=to_geojson_point(drift.origin_point),
        origin_probability_cone=to_geojson_polygon(drift.origin_probability_cone),
        origin_time_estimate=drift.origin_time_estimate,
        origin_confidence=drift.origin_confidence,
        hindcast_path=to_geojson_linestring(drift.hindcast_path),
        forward_path=None
    )

@router.post("/forecast", response_model=DriftResponse, status_code=status.HTTP_201_CREATED)
async def forecast(req: ForecastRequest, db: AsyncSession = Depends(get_db)):
    """Perform drift forecast to predict future spill trajectory (protected)."""
    drift = await calculate_forecast(db, req)
    return DriftResponse(
        origin_point=None,
        origin_probability_cone=None,
        origin_time_estimate=None,
        origin_confidence=None,
        hindcast_path=None,
        forward_path=to_geojson_linestring(drift.forecast_path)
    )
