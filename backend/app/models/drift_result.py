import uuid
from datetime import datetime, UTC
from sqlalchemy import Column, String, DateTime, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from app.core.database import Base

class DriftResult(Base):
    __tablename__ = "drift_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False)
    origin_point = Column(Geometry(geometry_type="POINT", srid=4326), nullable=True)
    origin_probability_cone = Column(Geometry(srid=4326), nullable=True) # Polygon/MultiPolygon
    origin_time_estimate = Column(DateTime, nullable=True)
    origin_confidence = Column(Float, nullable=True)
    hindcast_path = Column(Geometry(srid=4326), nullable=True) # LineString
    forecast_path = Column(Geometry(srid=4326), nullable=True) # LineString
    model_name = Column(String, nullable=True) # OpenDrift, GNOME, etc.
    model_version = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
