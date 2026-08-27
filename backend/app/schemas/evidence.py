from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel

class EvidenceItem(BaseModel):
    type: str # spatial, temporal, trajectory, ais_anomaly
    description: str

class DetectionEvidence(BaseModel):
    confidence: float

class OriginEvidence(BaseModel):
    confidence: float

class TopCandidateEvidence(BaseModel):
    vessel_id: UUID
    score: float

class EvidenceResponse(BaseModel):
    incident_id: UUID
    detection: Optional[DetectionEvidence] = None
    origin: Optional[OriginEvidence] = None
    top_candidate: Optional[TopCandidateEvidence] = None
    evidence: List[EvidenceItem] = []
