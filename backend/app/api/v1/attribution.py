from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.core.security import require_analyst
from app.schemas.attribution import ScoreRequest, AttributionResponse, VesselCandidateResponse
from app.services.attribution_service import calculate_attribution_scores
from app.models.attribution import AttributionScore
from app.models.vessel import Vessel

router = APIRouter(prefix="/attribution", tags=["Attribution Engine"], dependencies=[Depends(require_analyst)])

@router.get("", response_model=AttributionResponse)
async def list_attribution_scores(db: AsyncSession = Depends(get_db)):
    """List all attribution scores (protected)."""
    stmt = select(AttributionScore)
    res = await db.execute(stmt)
    scores = res.scalars().all()

    candidates = []
    for s in scores:
        stmt_v = select(Vessel).where(Vessel.id == s.vessel_id)
        res_v = await db.execute(stmt_v)
        vessel = res_v.scalars().first()

        candidates.append(VesselCandidateResponse(
            vessel_id=s.vessel_id,
            mmsi=vessel.mmsi if vessel else "",
            name=vessel.name if vessel else "Unknown Vessel",
            score=s.score,
            proximity=s.proximity_score,
            temporality=s.temporality_score,
            trajectory_parity=s.trajectory_score,
            anomaly_score=s.anomaly_score,
            anomaly_flag=s.anomaly_flag
        ))

    return AttributionResponse(ranked_vessels=candidates)

@router.post("/score", response_model=AttributionResponse, status_code=status.HTTP_201_CREATED)
async def score_vessels(req: ScoreRequest, db: AsyncSession = Depends(get_db)):
    """Calculate correlation scores for all vessels present near estimated origin (protected)."""
    scores = await calculate_attribution_scores(db, req)
    
    candidates = []
    for s in scores:
        # Get vessel name
        stmt = select(Vessel).where(Vessel.id == s.vessel_id)
        res = await db.execute(stmt)
        vessel = res.scalars().first()
        
        candidates.append(VesselCandidateResponse(
            vessel_id=s.vessel_id,
            mmsi=vessel.mmsi if vessel else "",
            name=vessel.name if vessel else "Unknown Vessel",
            score=s.score,
            proximity=s.proximity_score,
            temporality=s.temporality_score,
            trajectory_parity=s.trajectory_score,
            anomaly_score=s.anomaly_score,
            anomaly_flag=s.anomaly_flag
        ))
        
    return AttributionResponse(ranked_vessels=candidates)
