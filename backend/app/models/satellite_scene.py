import uuid
from datetime import datetime, UTC
from sqlalchemy import Column, String, DateTime, Text, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from geoalchemy2 import Geometry
from app.core.database import Base

class SatelliteScene(Base):
    __tablename__ = "satellite_scenes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Source identification
    source = Column(String, nullable=False) # e.g., 'sentinel-1-replay'
    scene_id = Column(String, nullable=False) # Source scene identifier like 'S1A_20250615_001'
    satellite = Column(String, nullable=False) # Sentinel-1, EOS-4, etc.
    sensor = Column(String, nullable=True) # SAR, etc.
    product_type = Column(String, nullable=False) # GRD, SLC, etc.
    polarization = Column(String, nullable=True) # VV, VV+VH, etc.
    # Timestamps
    acquisition_time = Column(DateTime(timezone=True), nullable=False) # When satellite captured the scene
    processing_time = Column(DateTime(timezone=True), nullable=True) # When data was processed
    # Geospatial
    bbox = Column(Geometry(geometry_type="POLYGON", srid=4326), nullable=False) # Bounding box as polygon
    # Image reference
    image_url = Column(String, nullable=True) # Location of image artifact
    thumbnail_url = Column(String, nullable=True) # Thumbnail preview
    # Metadata
    scene_metadata = Column(JSONB, nullable=True) # Additional provider metadata
    # Status tracking
    status = Column(String, nullable=False, default='RECEIVED') # RECEIVED, VALIDATING, INGESTED, QUEUED, FAILED, etc.
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    # Table arguments for constraints and indexes
    __table_args__ = (
        UniqueConstraint('source', 'scene_id', name='uix_source_scene_id'),
        Index('ix_satellite_scene_acquisition_time', 'acquisition_time'),
        Index('ix_satellite_scene_status', 'status'),
    )
