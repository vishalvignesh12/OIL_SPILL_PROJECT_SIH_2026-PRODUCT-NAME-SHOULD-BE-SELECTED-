from uuid import UUID
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from geoalchemy2.shape import to_shape
from shapely.geometry import mapping
from app.models.incident import Incident
from app.models.slick_detection import SlickDetection
from app.models.drift_result import DriftResult
from app.models.attribution import AttributionScore
from app.models.vessel import Vessel
from app.models.ais_track import AISTrack
from app.schemas.investigation import InvestigationResponse
from app.schemas.incident import IncidentResponse, GeoJSONPoint
from app.schemas.detection import DetectionResponse
from app.schemas.drift import DriftResponse, GeoJSONLineString
from app.schemas.scene import GeoJSONPolygon
from app.schemas.vessel import VesselResponse
from app.schemas.attribution import VesselCandidateResponse
from app.schemas.ais import AISGapAlert
from app.services.evidence_service import get_evidence
from app.services.ais_service import detect_ais_gaps, query_ais_tracks

def to_geojson_point(geom) -> Optional[GeoJSONPoint]:
    if geom is None:
        return None
    shape_obj = to_shape(geom)
    return GeoJSONPoint(coordinates=(shape_obj.x, shape_obj.y))

def to_geojson_polygon(geom) -> Optional[GeoJSONPolygon]:
    if geom is None:
        return None
    shape_obj = to_shape(geom)
    mapped = mapping(shape_obj)
    return GeoJSONPolygon(coordinates=mapped["coordinates"])

def to_geojson_linestring(geom) -> Optional[GeoJSONLineString]:
    if geom is None:
        return None
    shape_obj = to_shape(geom)
    mapped = mapping(shape_obj)
    return GeoJSONLineString(coordinates=mapped["coordinates"])

async def get_investigation_details(db: AsyncSession, incident_id: UUID) -> InvestigationResponse:
    """Compile a consolidated investigation payload containing incident, slick, drift, and attribution details."""
    # 1. Fetch Incident
    stmt = select(Incident).where(Incident.id == incident_id)
    res = await db.execute(stmt)
    incident = res.scalars().first()
    if not incident:
        return None
        
    incident_res = IncidentResponse(
        id=incident.id,
        name=incident.name,
        description=incident.description,
        timestamp=incident.timestamp,
        location=to_geojson_point(incident.location),
        status=incident.status,
        created_at=incident.created_at,
        updated_at=incident.updated_at
    )
    
    # 2. Fetch Slick Detection
    stmt = select(SlickDetection).where(SlickDetection.incident_id == incident_id)
    res = await db.execute(stmt)
    slick = res.scalars().first()
    slick_res = None
    if slick:
        slick_res = DetectionResponse(
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
        
    # 3. Fetch Drift Result (find hindcast/forecast)
    stmt = select(DriftResult).where(DriftResult.incident_id == incident_id)
    res = await db.execute(stmt)
    drifts = list(res.scalars().all())
    
    drift_res = None
    if drifts:
        # Find one that has hindcast or forecast
        hindcast_drift = next((d for d in drifts if d.hindcast_path is not None), drifts[0])
        forecast_drift = next((d for d in drifts if d.forecast_path is not None), None)
        
        drift_res = DriftResponse(
            origin_point=to_geojson_point(hindcast_drift.origin_point),
            origin_probability_cone=to_geojson_polygon(hindcast_drift.origin_probability_cone),
            origin_time_estimate=hindcast_drift.origin_time_estimate,
            origin_confidence=hindcast_drift.origin_confidence,
            hindcast_path=to_geojson_linestring(hindcast_drift.hindcast_path),
            forward_path=to_geojson_linestring(forecast_drift.forecast_path) if forecast_drift else to_geojson_linestring(hindcast_drift.forecast_path)
        )
        
    # 4. Fetch Attribution Candidates & Vessels
    stmt = select(AttributionScore).where(AttributionScore.incident_id == incident_id).order_by(AttributionScore.score.desc())
    res = await db.execute(stmt)
    scores = list(res.scalars().all())
    
    vessels_res = []
    attrib_res = []
    ais_alerts = []
    
    # Track points for all vessels present in timeframe
    # To compile gap alerts, we query tracks for the vessels
    all_tracks = await query_ais_tracks(db, incident.timestamp - timedelta(hours=12), incident.timestamp + timedelta(hours=12))
    
    for score in scores:
        stmt = select(Vessel).where(Vessel.id == score.vessel_id)
        v_res = await db.execute(stmt)
        vessel = v_res.scalars().first()
        
        if vessel:
            vessels_res.append(VesselResponse(
                id=vessel.id,
                mmsi=vessel.mmsi,
                imo=vessel.imo,
                name=vessel.name,
                type=vessel.type,
                flag=vessel.flag,
                length=vessel.length
            ))
            
            attrib_res.append(VesselCandidateResponse(
                vessel_id=score.vessel_id,
                mmsi=vessel.mmsi,
                name=vessel.name,
                score=score.score,
                proximity=score.proximity_score,
                temporality=score.temporality_score,
                trajectory_parity=score.trajectory_score,
                anomaly_score=score.anomaly_score,
                anomaly_flag=score.anomaly_flag
            ))
            
            # Find gap alerts for this vessel
            vessel_pts = [t for t in all_tracks if t.vessel_id == vessel.id]
            gaps = await detect_ais_gaps(vessel_pts, threshold_hours=2.0)
            for gap in gaps:
                ais_alerts.append(AISGapAlert(
                    anomaly_flag=True,
                    gap_start=gap["gap_start"],
                    gap_end=gap["gap_end"],
                    priority=gap["priority"],
                    explanation=f"{vessel.name}: {gap['explanation']}"
                ))
                
    # 5. Compile Evidence summary
    evidence_payload = await get_evidence(db, incident_id)
    
    return InvestigationResponse(
        incident=incident_res,
        slick=slick_res,
        drift=drift_res,
        vessels=vessels_res,
        attribution=attrib_res,
        ais_alerts=ais_alerts,
        evidence=evidence_payload.model_dump()
    )
