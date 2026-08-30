import uuid
from datetime import datetime, UTC
from sqlalchemy import Column, String, DateTime, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from app.core.database import Base

class AISTrack(Base):
    __tablename__ = "ais_tracks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vessel_id = Column(UUID(as_uuid=True), ForeignKey("vessels.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    position = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    speed = Column(Float, nullable=True) # Speed over ground in knots
    course = Column(Float, nullable=True) # Course over ground in degrees
    heading = Column(Float, nullable=True) # True heading in degrees
    source = Column(String, nullable=True) # GFW, MarineTraffic, CSV fixture, etc.
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
