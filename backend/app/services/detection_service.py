import time
from datetime import datetime, UTC
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2.shape import from_shape
from shapely.geometry import shape
from app.integrations.satellite import FixtureSatelliteAdapter
from app.models.slick_detection import SlickDetection
from app.models.inference_log import MLInferenceLog
from app.schemas.detection import AnalyzeRequest, DetectionResponse
from app.core.logging import log_inference

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
    
    # Save SlickDetection record
    # For MVP, we will try to resolve incident_id by looking up an active incident or create a mock association
    # We will assume caller links incident later, or use standard mock incident UUID if scene is seeded
    # We retrieve the incident ID from standard demo scenarios or req parameters
    # Let's verify: the slick_detection table has an incident_id foreign key.
    # To keep it robust, we look up or seed an incident if incident_id is not present or create one.
    # We can pass an optional incident_id or retrieve the incident_id from custom context.
    # For now, let's create a SlickDetection and assign the FK. Let's make sure our function receives the incident_id.
    # Wait, the POST /detections/analyze request is:
    # { "scene_id": "...", "image_url": "...", "timestamp": "..." }
    # Wait! How does it link to an incident?
    # PRD §12: POST /api/v1/detections/analyze. Request: scene_id, image_url, timestamp. Response: detection_id, slick_polygon, etc.
    # Wait, in the database schema, slick_detections has incident_id FK and scene_id FK.
    # If the incident doesn't exist yet, we can create a placeholder incident automatically so the whole chain works end-to-end!
    # That is extremely smart. If an incident exists for this scene, we link to it; otherwise we create a new Incident first.
    # Let's search if there is an incident with this timestamp or area. If not, create a new Incident.
    # Let's write this logic:
    from app.models.incident import Incident
    from sqlalchemy.future import select
    
    # Search for an existing incident matching scene_id or timestamp
    stmt = select(Incident).where(Incident.name.like(f"%{req.scene_id}%"))
    res = await db.execute(stmt)
    incident = res.scalars().first()
    
    if not incident:
        # Create a placeholder incident
        incident = Incident(
            name=f"Incident for Scene {req.scene_id}",
            description="Auto-generated incident from satellite scene analysis",
            timestamp=req.timestamp,
            location=from_shape(shape({"type": "Point", "coordinates": [76.11, 9.82]}), srid=4326),
            status="DETECTED"
        )
        db.add(incident)
        await db.flush() # get incident.id
        
    # Search if SatelliteScene metadata is registered
    from app.models.satellite_scene import SatelliteScene
    stmt = select(SatelliteScene).where(SatelliteScene.id == req.scene_id)
    # Wait, scene_id in req might be a UUID string or custom string. If not UUID, we can query by satellite metadata
    # Or create a placeholder SatelliteScene
    scene_uuid = None
    try:
        scene_uuid = UUID(req.scene_id)
    except ValueError:
        pass
        
    if scene_uuid:
        stmt = select(SatelliteScene).where(SatelliteScene.id == scene_uuid)
        res = await db.execute(stmt)
        scene = res.scalars().first()
    else:
        scene = None
        
    if not scene:
        # Create a placeholder scene
        scene = SatelliteScene(
            satellite="Sentinel-1",
            product_type="GRD",
            polarization="VV",
            timestamp=req.timestamp,
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
            thumbnail_url=req.image_url
        )
        db.add(scene)
        await db.flush()
        
    slick = SlickDetection(
        id=result["detection_id"],
        incident_id=incident.id,
        scene_id=scene.id,
        geometry=geom,
        area_km2=result["area_km2"],
        length_km=result["length_km"],
        width_km=result["width_km"],
        orientation_deg=result["orientation_deg"],
        confidence=result["confidence"],
        age_estimate_hours=result["age_estimate_hours"],
        age_confidence=result["age_confidence"]
    )
    db.add(slick)
    
    # Save ML Inference Log
    log = MLInferenceLog(
        service_name="slick_detection_service",
        request_payload={"scene_id": req.scene_id, "image_url": req.image_url, "timestamp": req.timestamp.isoformat()},
        response_payload={
            "detection_id": str(slick.id),
            "area_km2": slick.area_km2,
            "confidence": slick.confidence,
            "age_estimate_hours": slick.age_estimate_hours,
            "age_confidence": slick.age_confidence
        },
        model_name="UNet-ResNet34-SAR",
        model_version="v1.4.2",
        latency_ms=latency_ms,
        status="SUCCESS",
        timestamp=datetime.now(UTC)
    )
    db.add(log)
    
    # Commit changes
    await db.commit()
    await db.refresh(slick)
    
    # Log structured inference
    log_inference(
        service_name="slick_detection_service",
        model_name="UNet-ResNet34-SAR",
        model_version="v1.4.2",
        incident_id=str(incident.id),
        latency_ms=latency_ms,
        status_code=200
    )
    
    return slick
