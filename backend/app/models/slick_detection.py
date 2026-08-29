import uuid
from datetime import datetime, UTC
from sqlalchemy import Column, String, DateTime, Float, ForeignKey, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from sqlalchemy.orm import relationship
from app.core.database import Base

class SlickDetection(Base):
    __tablename__ = "slick_detections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False)
    scene_id = Column(UUID(as_uuid=True), ForeignKey("satellite_scenes.id", ondelete="SET NULL"), nullable=True)
    analysis_id = Column(String, nullable=False, index=True)  # Links to ML analysis job
    detected = Column(Boolean, nullable=False, default=True)  # Whether oil spill was detected
    confidence = Column(Float, nullable=False)  # 0 to 1
    model_version = Column(String, nullable=False)  # Version of ML model used
    processing_time_ms = Column(Integer, nullable=False)  # Processing time in milliseconds
    source_scene_id = Column(String, nullable=False)  # Original scene ID from data provider
    geometry = Column(Geometry(geometry_type="POLYGON", srid=4326), nullable=False)
    area_km2 = Column(Float, nullable=False)  # Area in square kilometers
    length_km = Column(Float, nullable=True)  # Length in kilometers
    width_km = Column(Float, nullable=True)  # Width in kilometers
    orientation_deg = Column(Float, nullable=True)  # Orientation in degrees
    mask_uri = Column(String, nullable=True)  # URI to segmentation mask in object storage
    prediction_uri = Column(String, nullable=True)  # URI to prediction output in object storage
    age_estimate_hours = Column(Float, nullable=True)  # Estimated age of oil spill in hours
    age_confidence = Column(String, nullable=True)  # Confidence in age estimate (e.g., "LOW", "HIGH")
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    # Relationship to SpillRegion
    regions = relationship("SpillRegion", back_populates="detection", cascade="all, delete-orphan")