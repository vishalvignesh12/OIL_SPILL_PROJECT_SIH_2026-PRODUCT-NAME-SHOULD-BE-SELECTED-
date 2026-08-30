from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import require_analyst
from app.schemas.attribution import ScoreRequest, AttributionResponse, VesselCandidateResponse
from app.services.attribution_service import calculate_attribution_scores
from app.models.vessel import Vessel
from sqlalchemy.future import select

router = APIRouter(prefix="/attribution", tags=["Attribution Engine"], dependencies=[Depends(require_analyst)])

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
