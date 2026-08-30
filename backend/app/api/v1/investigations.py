from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import require_analyst
from app.schemas.investigation import InvestigationResponse
from app.schemas.evidence import EvidenceResponse
from app.services.investigation_service import get_investigation_details
from app.services.evidence_service import get_evidence, generate_csv_export

router = APIRouter(prefix="/investigations", tags=["Investigations Workspace"], dependencies=[Depends(require_analyst)])

@router.get("/{incident_id}", response_model=InvestigationResponse)
async def get_investigation(incident_id: UUID, db: AsyncSession = Depends(get_db)):
    """Retrieve consolidated data for the investigation workspace (protected)."""
    details = await get_investigation_details(db, incident_id)
    if not details:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investigation/incident not found")
    return details

@router.get("/{incident_id}/evidence", response_model=EvidenceResponse)
async def get_investigation_evidence(incident_id: UUID, db: AsyncSession = Depends(get_db)):
    """Compile audit and correlation evidence for the incident (protected)."""
    evidence = await get_evidence(db, incident_id)
    return evidence

@router.get("/{incident_id}/export")
async def export_investigation_csv(incident_id: UUID, db: AsyncSession = Depends(get_db)):
    """Export ranked vessel attribution data in CSV format (protected)."""
    csv_str = await generate_csv_export(db, incident_id)
    
    filename = f"evidence_{incident_id}.csv"
    headers = {
        "Content-Disposition": f"attachment; filename={filename}"
    }
    
    return Response(content=csv_str, media_type="text/csv", headers=headers)
