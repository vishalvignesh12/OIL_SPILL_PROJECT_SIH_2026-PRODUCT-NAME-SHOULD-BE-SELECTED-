import uuid
import hashlib
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from geoalchemy2.shape import from_shape
from shapely.geometry import shape, mapping
import json

from app.models.satellite_scene import SatelliteScene
from app.schemas.scene import SceneCreate
from app.core.config import settings
from app.core.logging import log_inference
from app.integrations.satellite import FixtureSatelliteAdapter


async def validate_scene_metadata(req: SceneCreate) -> Dict[str, Any]:
    """
    Validate satellite scene metadata according to specification.
    Returns normalized metadata or raises validation errors.
    """
    errors = []

    # Validate source
    if not req.source or len(req.source.strip()) == 0:
        errors.append("source is required and cannot be empty")

    # Validate scene_id
    if not req.scene_id or len(req.scene_id.strip()) == 0:
        errors.append("scene_id is required and cannot be empty")

    # Validate acquisition_time (should not be too far in the future)
    now = datetime.now(timezone.utc)
    if req.acquisition_time > now:
        # Allow some tolerance for clock differences
        time_diff = req.acquisition_time - now
        if time_diff.total_seconds() > 3600:  # 1 hour tolerance
            errors.append("acquisition_time cannot be more than 1 hour in the future")

    # Validate bbox coordinates
    try:
        bbox_dict = req.bbox.model_dump()
        coordinates = bbox_dict.get("coordinates", [])
        if not coordinates or len(coordinates) == 0:
            errors.append("bbox must contain at least one coordinate ring")
        else:
            # Validate each coordinate ring
            for i, ring in enumerate(coordinates):
                if len(ring) < 4:
                    errors.append(f"bbox coordinate ring {i} must have at least 4 points")
                # Check if ring is closed (first point == last point)
                if len(ring) >= 4 and ring[0] != ring[-1]:
                    errors.append(f"bbox coordinate ring {i} must be closed (first point == last point)")

                # Validate each coordinate
                for j, coord in enumerate(ring):
                    if len(coord) != 2:
                        errors.append(f"bbox coordinate {i},{j} must be [longitude, latitude]")
                    else:
                        lon, lat = coord
                        if not (-180 <= lon <= 180):
                            errors.append(f"bbox coordinate {i},{j} longitude {lon} must be between -180 and 180")
                        if not (-90 <= lat <= 90):
                            errors.append(f"bbox coordinate {i},{j} latitude {lat} must be between -90 and 90")

                # Validate geographic bounds
                min_lon = min(coord[0] for coord in ring)
                max_lon = max(coord[0] for coord in ring)
                min_lat = min(coord[1] for coord in ring)
                max_lat = max(coord[1] for coord in ring)

                if min_lon >= max_lon:
                    errors.append(f"bbox coordinate ring {i} min_lon must be less than max_lon")
                if min_lat >= max_lat:
                    errors.append(f"bbox coordinate ring {i} min_lat must be less than max_lat")
    except Exception as e:
        errors.append(f"Invalid bbox format: {str(e)}")

    # Validate image_uri/image_url
    if not req.image_url or len(req.image_url.strip()) == 0:
        errors.append("image_url is required and cannot be empty")
    else:
        # Basic URI validation
        image_url = req.image_url.strip()
        allowed_schemes = ["http", "https", "file", "storage", "s3"]
        if not any(image_url.startswith(scheme + "://") for scheme in allowed_schemes):
            # Allow relative paths for development
            if not image_url.startswith("/"):
                errors.append(f"image_url must use one of the allowed schemes: {allowed_schemes} or be an absolute path")

    if errors:
        raise ValueError(f"Validation failed: {'; '.join(errors)}")

    # Return normalized metadata
    return {
        "source": req.source.strip(),
        "scene_id": req.scene_id.strip(),
        "satellite": req.satellite.strip(),
        "sensor": req.sensor.strip() if req.sensor else None,
        "product_type": req.product_type.strip(),
        "polarization": req.polarization.strip() if req.polarization else None,
        "acquisition_time": req.acquisition_time,
        "processing_time": req.processing_time,
        "bbox": req.bbox,
        "image_url": req.image_url,
        "thumbnail_url": req.thumbnail_url,
        "scene_metadata": req.scene_metadata or {},
        "status": "RECEIVED"
    }


async def check_duplicate_scene(db: AsyncSession, source: str, scene_id: str) -> bool:
    """
    Check if a scene with the same source and scene_id already exists.
    Returns True if duplicate exists, False otherwise.
    """
    stmt = select(SatelliteScene).where(
        and_(
            SatelliteScene.source == source,
            SatelliteScene.scene_id == scene_id
        )
    )
    res = await db.execute(stmt)
    existing = res.scalars().first()
    return existing is not None


async def persist_satellite_scene(db: AsyncSession, scene_data: Dict[str, Any]) -> SatelliteScene:
    """
    Persist the satellite scene to the database.
    """
    # Convert GeoJSON polygon to Shapely shape and then to GeoAlchemy2 element
    bbox_geojson = scene_data["bbox"].model_dump()
    geom = from_shape(shape(bbox_geojson), srid=4326)

    scene = SatelliteScene(
        source=scene_data["source"],
        scene_id=scene_data["scene_id"],
        satellite=scene_data["satellite"],
        sensor=scene_data["sensor"],
        product_type=scene_data["product_type"],
        polarization=scene_data["polarization"],
        acquisition_time=scene_data["acquisition_time"],
        processing_time=scene_data["processing_time"],
        bbox=geom,
        image_url=scene_data["image_url"],
        thumbnail_url=scene_data["thumbnail_url"],
        scene_metadata=scene_data["scene_metadata"],
        status=scene_data["status"]
    )

    db.add(scene)
    await db.flush()  # Get the ID without committing yet
    await db.refresh(scene)
    return scene


async def create_analysis_job(scene: SatelliteScene) -> str:
    """
    Create an analysis job for the ingested scene.
    In a real implementation, this would publish to a message queue.
    For MVP, we'll generate a job ID and return it.
    """
    # Generate a unique analysis ID
    # Could use UUID, or a simple incremental ID, or a hash
    analysis_id = str(uuid.uuid4())

    # In a real implementation, we would:
    # 1. Publish an event to a message queue (RabbitMQ, AWS SQS, etc.)
    # 2. The event would contain scene metadata and analysis_id
    # 3. An AI worker would consume the event and start processing

    # For logging purposes
    log_inference(
        service_name="satellite_ingestion_service",
        model_name="FixtureSceneIngestion",
        model_version="v1.0.0",
        incident_id="",  # Not available at ingestion time
        latency_ms=0,
        status_code=202  # Accepted for processing
    )

    return analysis_id


async def ingest_satellite_scene(db: AsyncSession, req: SceneCreate) -> Dict[str, Any]:
    """
    Main satellite ingestion function that orchestrates the ingestion process.
    """
    try:
        # Step 1: Validate metadata
        scene_data = await validate_scene_metadata(req)

        # Step 2: Check for duplicates
        is_duplicate = await check_duplicate_scene(
            db,
            scene_data["source"],
            scene_data["scene_id"]
        )

        if is_duplicate:
            # Update status to indicate duplicate was detected
            scene_data["status"] = "DUPLICATE_DETECTED"
            # For duplicates, we don't create a new record but return existing info

            # Get existing scene
            stmt = select(SatelliteScene).where(
                and_(
                    SatelliteScene.source == scene_data["source"],
                    SatelliteScene.scene_id == scene_data["scene_id"]
                )
            )
            res = await db.execute(stmt)
            existing_scene = res.scalars().first()

            if existing_scene:
                # Update the timestamp to show when it was re-received
                existing_scene.updated_at = datetime.now(timezone.utc)
                await db.commit()
                await db.refresh(existing_scene)

                return {
                    "success": True,
                    "scene_id": existing_scene.scene_id,
                    "analysis_id": f"existing_{existing_scene.id}",
                    "status": existing_scene.status,
                    "message": "Satellite scene already exists (duplicate detected)",
                    "is_duplicate": True
                }

        # Step 3: Persist the scene
        scene = await persist_satellite_scene(db, scene_data)

        # Step 4: Create analysis job
        analysis_id = await create_analysis_job(scene)

        # Step 5: Update scene status to indicate it's queued for analysis
        scene.status = "QUEUED"
        scene.updated_at = datetime.now(timezone.utc)

        # Commit all changes
        await db.commit()
        await db.refresh(scene)

        return {
            "success": True,
            "scene_id": scene.scene_id,
            "analysis_id": analysis_id,
            "status": scene.status,
            "message": "Satellite scene successfully ingested and queued for analysis",
            "is_duplicate": False
        }

    except Exception as e:
        await db.rollback()
        # Log the error
        log_inference(
            service_name="satellite_ingestion_service",
            model_name="FixtureSceneIngestion",
            model_version="v1.0.0",
            incident_id="",
            latency_ms=0,
            status_code=500
        )
        raise e