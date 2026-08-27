import uuid
from datetime import datetime, UTC
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from app.core.database import Base

class SatelliteScene(Base):
    __tablename__ = "satellite_scenes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    satellite = Column(String, nullable=False) # Sentinel-1, EOS-4, etc.
    product_type = Column(String, nullable=False) # GRD, SLC, etc.
    polarization = Column(String, nullable=False) # VV, VV+VH, etc.
    timestamp = Column(DateTime, nullable=False)
    bbox = Column(Geometry(geometry_type="POLYGON", srid=4326), nullable=False)
    image_url = Column(String, nullable=True)
    thumbnail_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
