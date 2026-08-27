import csv
import io
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.slick_detection import SlickDetection
from app.models.drift_result import DriftResult
from app.models.attribution import AttributionScore
from app.models.vessel import Vessel
from app.schemas.evidence import EvidenceResponse, EvidenceItem, DetectionEvidence, OriginEvidence, TopCandidateEvidence

async def get_evidence(db: AsyncSession, incident_id: UUID) -> EvidenceResponse:
    """Compile audit and correlation evidence for an incident."""
    # Query slick detection
    stmt = select(SlickDetection).where(SlickDetection.incident_id == incident_id)
    res = await db.execute(stmt)
    slick = res.scalars().first()
    
    # Query drift result
    stmt = select(DriftResult).where(DriftResult.incident_id == incident_id)
    res = await db.execute(stmt)
    drift = res.scalars().first()
    
    # Query attribution scores
    stmt = select(AttributionScore).where(AttributionScore.incident_id == incident_id).order_by(AttributionScore.score.desc())
    res = await db.execute(stmt)
    scores = list(res.scalars().all())
    
    det_ev = DetectionEvidence(confidence=slick.confidence) if slick else None
    orig_ev = OriginEvidence(confidence=drift.origin_confidence) if drift and drift.origin_confidence else None
    
    top_candidate = None
    evidence_items = []
    
    if scores:
        top = scores[0]
        top_candidate = TopCandidateEvidence(vessel_id=top.vessel_id, score=top.score)
        
        # Build specific evidence items for top candidate
        # Get vessel name
        stmt = select(Vessel).where(Vessel.id == top.vessel_id)
        v_res = await db.execute(stmt)
        vessel = v_res.scalars().first()
        vessel_name = vessel.name if vessel else "Top Candidate"
        
        if top.proximity_score >= 0.7:
            evidence_items.append(EvidenceItem(
                type="spatial",
                description=f"{vessel_name} passed within the estimated origin region (proximity score: {top.proximity_score})."
            ))
        if top.temporality_score >= 0.7:
            evidence_items.append(EvidenceItem(
                type="temporal",
                description=f"{vessel_name} was present within the estimated spill time window (temporality score: {top.temporality_score})."
            ))
        if top.trajectory_score >= 0.7:
            evidence_items.append(EvidenceItem(
                type="trajectory",
                description=f"{vessel_name}'s trajectory heading aligned with the slick orientation (alignment score: {top.trajectory_score})."
            ))
        if top.anomaly_flag:
            evidence_items.append(EvidenceItem(
                type="ais_anomaly",
                description=f"A critical AIS gap was detected for {vessel_name} overlapping the spill window (anomaly score: {top.anomaly_score})."
            ))
            
    return EvidenceResponse(
        incident_id=incident_id,
        detection=det_ev,
        origin=orig_ev,
        top_candidate=top_candidate,
        evidence=evidence_items
    )

async def generate_csv_export(db: AsyncSession, incident_id: UUID) -> str:
    """Generate CSV string containing attribution scores for an incident."""
    stmt = select(AttributionScore).where(AttributionScore.incident_id == incident_id).order_by(AttributionScore.score.desc())
    res = await db.execute(stmt)
    scores = res.scalars().all()
    
    # Get incident timestamp
    from app.models.incident import Incident
    stmt = select(Incident).where(Incident.id == incident_id)
    i_res = await db.execute(stmt)
    incident = i_res.scalars().first()
    incident_ts = incident.timestamp.isoformat() if incident else ""
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Headers matching PRD §20
    writer.writerow([
        "incident_id",
        "incident_timestamp",
        "vessel_id",
        "vessel_name",
        "mmsi",
        "attribution_score",
        "proximity",
        "temporality",
        "trajectory_parity",
        "anomaly_flag"
    ])
    
    for score in scores:
        # Get vessel details
        stmt = select(Vessel).where(Vessel.id == score.vessel_id)
        v_res = await db.execute(stmt)
        vessel = v_res.scalars().first()
        
        writer.writerow([
            str(incident_id),
            incident_ts,
            str(score.vessel_id),
            vessel.name if vessel else "",
            vessel.mmsi if vessel else "",
            score.score,
            score.proximity_score,
            score.temporality_score,
            score.trajectory_score,
            "true" if score.anomaly_flag else "false"
        ])
        
    return output.getvalue()
