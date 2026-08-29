
from datetime import datetime, timedelta, UTC
from typing import List, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from geoalchemy2.shape import to_shape
from geoalchemy2.elements import WKBElement, WKTElement
from shapely.geometry.base import BaseGeometry
from shapely.geometry import shape, Point, LineString
import math
from app.models.vessel import Vessel
from app.models.attribution import AttributionScore
from app.models.drift_result import DriftResult
from app.schemas.attribution import ScoreRequest, AttributionResponse, VesselCandidateResponse
from app.services.ais_service import query_ais_tracks, detect_ais_gaps

from sqlalchemy.orm import aliased

async def calculate_attribution_scores(db: AsyncSession, req: ScoreRequest) -> List[AttributionScore]:
    """Calculate ranked vessel attribution scores using PostGIS AIS tracks."""
    # Convert origin point to Shapely object
    origin_shp = shape(req.origin_point.model_dump())
    
    # Fetch drift result if available to get hindcast path alignment
    stmt_drift = select(DriftResult).where(DriftResult.incident_id == req.incident_id)
    res_drift = await db.execute(stmt_drift)
    drift_result = res_drift.scalars().first()
    
    spill_angle = 53.0
    has_drift_path = False
    if drift_result and drift_result.hindcast_path:
        hp = drift_result.hindcast_path
        if isinstance(hp, BaseGeometry):
            hp_shp = hp
        elif isinstance(hp, (WKBElement, WKTElement)):
            hp_shp = to_shape(hp)
        else:
            hp_shp = None
            
        if hp_shp and hasattr(hp_shp, "coords") and len(hp_shp.coords) >= 2:
            dx_spill = hp_shp.coords[-1][0] - hp_shp.coords[0][0]
            dy_spill = hp_shp.coords[-1][1] - hp_shp.coords[0][1]
            spill_angle = math.degrees(math.atan2(dy_spill, dx_spill)) % 360
            has_drift_path = True

    # 1. PostGIS spatial+temporal AIS search (via query_ais_tracks)
    # We broaden the temporal search by 12 hours to capture tracks leading up to and after the spill
    buffer_start = req.origin_time_start - timedelta(hours=12)
    buffer_end = req.origin_time_end + timedelta(hours=12)
    
    tracks = await query_ais_tracks(db, buffer_start, buffer_end)
    
    # Group tracks by vessel ID
    vessel_tracks: Dict[UUID, List[Any]] = {}
    for track in tracks:
        vessel_tracks.setdefault(track.vessel_id, []).append(track)
        
    results = []
    
    for vessel_id, track_pts in vessel_tracks.items():
        # Get Vessel info
        stmt = select(Vessel).where(Vessel.id == vessel_id)
        res = await db.execute(stmt)
        vessel = res.scalars().first()
        if not vessel:
            continue
            
        # 1. Spatial Proximity
        # Find minimum distance to origin
        min_dist_km = 9999.0
        nearest_time = None
        
        # Sort track points by time
        track_pts = sorted(track_pts, key=lambda t: t.timestamp)
        coords = []
        
        for pt in track_pts:
            if isinstance(pt.position, BaseGeometry):
                pt_shp = pt.position
            elif isinstance(pt.position, (WKBElement, WKTElement)):
                pt_shp = to_shape(pt.position)
            elif hasattr(pt.position, "x") and hasattr(pt.position, "y") and isinstance(getattr(pt.position, "x", None), (int, float)):
                pt_shp = Point(pt.position.x, pt.position.y)
            else:
                # Skip track points with invalid/missing position geometry
                continue
            coords.append((pt_shp.x, pt_shp.y))
            # Rough distance in km (1 degree approx 111 km at equator)
            dist = origin_shp.distance(pt_shp) * 111.0
            if dist < min_dist_km:
                min_dist_km = dist
                nearest_time = pt.timestamp
                
        # Spatial score: 1.0 at 0km, 0.0 at 20km or more
        spatial_proximity = max(0.0, 1.0 - (min_dist_km / 20.0))
        
        # 2. Temporal Match
        # Time diff between nearest point and origin window center
        origin_center = req.origin_time_start + (req.origin_time_end - req.origin_time_start) / 2
        if nearest_time:
            time_diff_hours = abs((nearest_time - origin_center).total_seconds()) / 3600.0
            # Temporal score: 1.0 within 1h, 0.0 at 12h or more
            temporal_match = max(0.0, 1.0 - (time_diff_hours / 12.0))
        else:
            temporal_match = 0.0
            
        # 3. Trajectory Parity / Alignment
        # Calculate heading of vessel path if it has at least 2 points
        if len(coords) >= 2:
            # Vector of vessel track
            dx = coords[-1][0] - coords[0][0]
            dy = coords[-1][1] - coords[0][1]
            track_angle = math.degrees(math.atan2(dy, dx)) % 360
            
            angle_diff = abs(track_angle - spill_angle)
            if angle_diff > 180:
                angle_diff = 360 - angle_diff
            # Trajectory score: 1.0 aligned, 0.0 perpendicular/opposite
            trajectory_alignment = max(0.0, 1.0 - (angle_diff / 90.0))
        elif has_drift_path:
            trajectory_alignment = 0.75
        else:
            trajectory_alignment = 0.5
            
        # 4. AIS Anomaly / Gap Score
        # Check if there is an AIS gap during the spill window
        vessel_gaps = await detect_ais_gaps(track_pts, threshold_hours=2.0)
        has_overlap_gap = False
        for gap in vessel_gaps:
            # Overlap exists if gap starts before window end and ends after window start
            if gap["gap_start"] <= req.origin_time_end and gap["gap_end"] >= req.origin_time_start:
                has_overlap_gap = True
                break
                
        ais_anomaly = 1.0 if has_overlap_gap else 0.0
        
        # Combined score formula (PRD §16):
        # 0.30 * spatial + 0.30 * temporal + 0.25 * trajectory + 0.15 * anomaly
        combined_score = (
            0.30 * spatial_proximity +
            0.30 * temporal_match +
            0.25 * trajectory_alignment +
            0.15 * ais_anomaly
        )
        
        # Round scores to 2 decimals
        combined_score = round(combined_score, 2)
        spatial_proximity = round(spatial_proximity, 2)
        temporal_match = round(temporal_match, 2)
        trajectory_alignment = round(trajectory_alignment, 2)
        ais_anomaly = round(ais_anomaly, 2)
        
        # Save Attribution Score
        # Delete existing score for this incident-vessel combo if exists
        stmt = select(AttributionScore).where(
            AttributionScore.incident_id == req.incident_id,
            AttributionScore.vessel_id == vessel_id
        )
        res = await db.execute(stmt)
        existing = res.scalars().first()
        if existing:
            await db.delete(existing)
            
        score_record = AttributionScore(
            incident_id=req.incident_id,
            vessel_id=vessel_id,
            score=combined_score,
            proximity_score=spatial_proximity,
            temporality_score=temporal_match,
            trajectory_score=trajectory_alignment,
            anomaly_score=ais_anomaly,
            anomaly_flag=has_overlap_gap,
            explanation=f"Vessel passed within {min_dist_km:.2f} km of estimated origin. " + (
                "An AIS gap was detected overlapping the spill window." if has_overlap_gap else "AIS transmission was continuous."
            )
        )
        db.add(score_record)
        results.append(score_record)
        
    await db.commit()
    
    # Sort results descending by score
    results = sorted(results, key=lambda s: s.score, reverse=True)
    return results
