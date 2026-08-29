import time
from datetime import datetime, UTC
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from geoalchemy2.shape import from_shape
from shapely.geometry import shape
from app.integrations.satellite import FixtureSatelliteAdapter
from app.models.slick_detection import SlickDetection
from app.models.incident import Incident
from app.models.satellite_scene import SatelliteScene
from app.models.inference_log import MLInferenceLog
from app.schemas.detection import AnalyzeRequest, DetectionResponse

async def analyze_slick(db: AsyncSession, req: AnalyzeRequest) -> SlickDetection:
    """Orchestrate satellite scene analysis, log inference, and save results."""
    start_time = time.time()
    
    # Instantiate satellite adapter (fixture version for MVP)
    adapter = FixtureSatelliteAdapter()
    
    # Run analysis
    result = await adapter.analyze_scene(req.scene_id, req.image_url or "", req.timestamp)
    latency_ms = int((time.time() - start_time) * 1000)
    
    # Convert GeoJSON polygon to Shapely shape and then to GeoAlchemy2 element
    slick_polygon_geojson = result["slick_polygon"]
    geom = from_shape(shape(slick_polygon_geojson), srid=4326)
    
    # Search for an existing incident matching scene_id
    stmt_inc = select(Incident).where(Incident.name.like(f"%{req.scene_id}%"))
    res_inc = await db.execute(stmt_inc)
    incident = res_inc.scalars().first()
    
    if not incident:
        incident = Incident(
            name=f"Incident for Scene {req.scene_id}",
            description="Auto-generated incident from satellite scene analysis",
            timestamp=req.timestamp,
            location=from_shape(shape({"type": "Point", "coordinates": [76.11, 9.82]}), srid=4326),
            status="DETECTED"
        )
        db.add(incident)
        await db.flush()
        
    scene_uuid = None
    try:
        scene_uuid = UUID(req.scene_id)
    except ValueError:
        pass
        
    if scene_uuid:
        stmt_scene = select(SatelliteScene).where(SatelliteScene.id == scene_uuid)
        res_scene = await db.execute(stmt_scene)
        scene = res_scene.scalars().first()
    else:
        scene = None
        
    if not scene:
        scene = SatelliteScene(
            source="sentinel-1-replay",
            scene_id=req.scene_id,
            satellite="Sentinel-1",
            sensor="SAR",
            product_type="GRD",
            polarization="VV",
            acquisition_time=req.timestamp,
            processing_time=datetime.now(UTC),
            bbox=from_shape(shape({
                "type": "Polygon",
                "coordinates": [[
                    [75.80, 9.50],
                    [76.40, 9.50],
                    [76.40, 10.10],
                    [75.80, 10.10],
                    [75.80, 9.50]
                ]]
            }), srid=4326),
            image_url=req.image_url,
            thumbnail_url=req.image_url,
            status="INGESTED",
        )
        db.add(scene)
        await db.flush()

    slick = SlickDetection(
        incident_id=incident.id,
        scene_id=scene.id,
        geometry=geom,
        area_km2=result["area_km2"],
        length_km=result.get("length_km"),
        width_km=result.get("width_km"),
        orientation_deg=result.get("orientation_deg"),
        confidence=result["confidence"],
        age_estimate_hours=result.get("age_estimate_hours"),
        age_confidence=result.get("age_confidence")
    )
    db.add(slick)
    await db.commit()
    await db.refresh(slick)
    
    return slick