from datetime import datetime, timedelta, timezone
from typing import Dict, Any
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.core.database import get_db
from app.core.security import require_analyst
from app.models.incident import Incident
from app.models.vessel import Vessel
from app.models.slick_detection import SlickDetection
from app.models.ais_track import AISTrack
from app.models.attribution import AttributionScore
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/metrics", response_model=Dict[str, Any])
async def get_system_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_analyst)
):
    """Get system-wide metrics and KPIs for dashboard overview."""

    # Count active incidents (last 7 days)
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    active_incidents_stmt = select(func.count(Incident.id)).where(
        and_(Incident.timestamp >= week_ago, Incident.status != "Closed / Actioned")
    )
    active_incidents_result = await db.execute(active_incidents_stmt)
    active_incidents = active_incidents_result.scalar() or 0

    # Count total vessels
    total_vessels_stmt = select(func.count(Vessel.id))
    total_vessels_result = await db.execute(total_vessels_stmt)
    total_vessels = total_vessels_result.scalar() or 0

    # Count verified slicks (detections with high confidence and attributed status)
    verified_slicks_stmt = select(func.count(SlickDetection.id)).where(
        and_(
            SlickDetection.confidence >= 80,
            SlickDetection.status.in_(["Attributed", "Closed / Actioned"])
        )
    )
    verified_slicks_result = await db.execute(verified_slicks_stmt)
    verified_slicks = verified_slicks_result.scalar() or 0

    # Calculate attribution rate (percentage of detections that are attributed)
    total_detections_stmt = select(func.count(SlickDetection.id))
    total_detections_result = await db.execute(total_detections_stmt)
    total_detections = total_detections_result.scalar() or 1  # Avoid division by zero

    attributed_detections_stmt = select(func.count(SlickDetection.id)).where(
        SlickDetection.status == "Attributed"
    )
    attributed_detections_result = await db.execute(attributed_detections_stmt)
    attributed_detections = attributed_detections_result.scalar() or 0

    attribution_rate = (attributed_detections / total_detections) * 100 if total_detections > 0 else 0

    # Count monitored vessels (vessels with recent AIS tracks)
    day_ago = datetime.now(timezone.utc) - timedelta(days=1)
    monitored_vessels_stmt = select(func.count(func.distinct(AISTrack.vessel_id))).where(
        AISTrack.timestamp >= day_ago
    )
    monitored_vessels_result = await db.execute(monitored_vessels_stmt)
    monitored_vessels = monitored_vessels_result.scalar() or 0

    # Calculate surveillance coverage (percentage of vessels with recent tracks)
    surveillance_coverage = (monitored_vessels / total_vessels * 100) if total_vessels > 0 else 0

    # Get most recent satellite pass (would come from satellite_scene table in real implementation)
    # For now, we'll use a placeholder
    last_satellite_pass = "Sentinel-1A (18 mins ago)"

    # System health (would be calculated from various health checks in real implementation)
    system_health = "100% Online"

    return {
        "activeIncidents": active_incidents,
        "activeIncidentsChange": f"+{max(0, active_incidents - 2)} this week",  # Placeholder calculation
        "monitoredVessels": monitored_vessels,
        "monitoredVesselsChange": f"+{max(0, int((monitored_vessels / max(total_vessels, 1) * 100) - 90))}% vs last 24h",  # Placeholder
        "verifiedSlicks": verified_slicks,
        "verifiedSlicksArea": f"{verified_slicks * 15.6:.1f} km² total",  # Rough estimate
        "attributionRate": f"{attribution_rate:.1f}%",
        "attributionRateStatus": "High confidence" if attribution_rate >= 90 else "Medium confidence" if attribution_rate >= 70 else "Low confidence",
        "surveillanceCoverage": f"{surveillance_coverage:.1f}%",
        "surveillanceStatus": "Operational" if surveillance_coverage >= 95 else "Degraded" if surveillance_coverage >= 80 else "Limited",
        "lastSatellitePass": last_satellite_pass,
        "systemHealth": system_health
    }

@router.get("/alerts")
async def get_security_alerts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_analyst)
):
    """Get security alerts for the dashboard."""
    # In a real implementation, this would come from an alerts table
    # For now, we'll generate some sample alerts based on recent activities

    # Get recent high-confidence attributions as alerts
    recent_attributions_stmt = select(AttributionScore).where(
        AttributionScore.combined_score >= 80
    ).order_by(AttributionScore.timestamp.desc()).limit(10)

    recent_attributions_result = await db.execute(recent_attributions_stmt)
    recent_attributions = recent_attributions_result.scalars().all()

    alerts = []
    for i, attribution in enumerate(recent_attributions):
        # Get incident info
        incident_stmt = select(Incident).where(Incident.id == attribution.incident_id)
        incident_result = await db.execute(incident_stmt)
        incident = incident_result.scalar_one_or_none()

        # Get vessel info
        vessel_stmt = select(Vessel).where(Vessel.id == attribution.vessel_id)
        vessel_result = await db.execute(vessel_stmt)
        vessel = vessel_result.scalar_one_or_none()

        if incident and vessel:
            alert = {
                "id": f"ALT-{20260827000 + i}",
                "incidentId": str(incident.id),
                "timestamp": attribution.timestamp.isoformat().replace("+00:00", " UTC"),
                "severity": "Critical" if attribution.combined_score >= 90 else "High" if attribution.combined_score >= 70 else "Medium",
                "title": f"High-Confidence Slick Attribution: {vessel.name} ({int(attribution.combined_score)}%)",
                "description": f"Spatial-temporal back-trajectory analysis overlaps with slick polygon in {incident.region}.",
                "acknowledged": i % 2 == 0,  # Alternate acknowledged/unacked for demo
                "acknowledgedBy": "Lt. A. Sharma (04:18 UTC)" if i % 2 == 0 else None
            }
            alerts.append(alert)

    # Add a few more generic alerts
    alerts.extend([
        {
            "id": "ALT-20260827010",
            "incidentId": str(recent_attributions[0].incident_id) if recent_attributions else "INC-2026-001",
            "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat().replace("+00:00", " UTC"),
            "severity": "Critical",
            "title": "Satellite SAR Anomaly Detection — Bay of Bengal",
            "description": "Sentinel-1A pass captured 46.8 km² slick polygon at 14°49'17\"N, 88°17'29\"E.",
            "acknowledged": True,
            "acknowledgedBy": "Lt. A. Sharma (04:18 UTC)"
        },
        {
            "id": "ALT-20260827011",
            "incidentId": str(recent_attributions[0].incident_id) if recent_attributions else "INC-2026-001",
            "timestamp": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat().replace("+00:00", " UTC"),
            "severity": "High",
            "title": "Potential Bilge Dump in Arabian Sea EEZ Boundary",
            "description": "Synthetic aperture radar detected 18.2 km² plume along international shipping lane.",
            "acknowledged": True,
            "acknowledgedBy": "Duty Officer K. Nair (19:50 UTC)"
        }
    ])

    return alerts

@router.get("/incidents/{incident_id}/map-layers")
async def get_incident_map_layers(
    incident_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_analyst)
):
    """Get pre-computed map layers for an incident."""
    # Get incident
    incident_stmt = select(Incident).where(Incident.id == incident_id)
    incident_result = await db.execute(incident_stmt)
    incident = incident_result.scalar_one_or_none()

    if not incident:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Incident not found")

    # In a real implementation, these would be stored or computed from detections
    # For now, we'll return sample data similar to the mock data
    return {
        "incidentCenter": [incident.latitude, incident.longitude] if incident.latitude and incident.longitude else [14.8214, 88.2915],
        "slickPolygonCoordinates": [
            [14.8850, 88.1920],
            [14.8980, 88.2450],
            [14.8620, 88.3580],
            [14.8120, 88.3980],
            [14.7750, 88.3450],
            [14.7920, 88.2410],
            [14.8350, 88.1850]
        ],
        "eezBoundaryCoordinates": [
            [16.5000, 86.0000],
            [15.8000, 87.5000],
            [14.2000, 89.2000],
            [12.8000, 90.5000]
        ],
        "shippingLaneCoordinates": [
            [14.5000, 86.5000],
            [14.7500, 88.0000],
            [14.8500, 88.5000],
            [15.1000, 90.0000]
        ]
    }