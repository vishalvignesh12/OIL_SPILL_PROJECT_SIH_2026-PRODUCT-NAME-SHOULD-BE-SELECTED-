from typing import List, Optional
from pydantic import BaseModel
from app.schemas.incident import IncidentResponse
from app.schemas.detection import DetectionResponse
from app.schemas.drift import DriftResponse
from app.schemas.vessel import VesselResponse
from app.schemas.attribution import VesselCandidateResponse
from app.schemas.ais import AISGapAlert

class InvestigationResponse(BaseModel):
    incident: IncidentResponse
    slick: Optional[DetectionResponse] = None
    drift: Optional[DriftResponse] = None
    vessels: List[VesselResponse] = []
    attribution: List[VesselCandidateResponse] = []
    ais_alerts: List[AISGapAlert] = []
    evidence: Optional[dict] = None
