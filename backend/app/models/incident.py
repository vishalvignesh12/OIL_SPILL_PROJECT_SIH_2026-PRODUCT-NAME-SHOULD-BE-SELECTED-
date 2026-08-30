import uuid
from datetime import datetime, UTC
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from app.core.database import Base

class Incident(Base):
    __tablename__ = "incidents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    location = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    status = Column(String, nullable=False, default="DETECTED") # DETECTED, INVESTIGATING, VERIFIED
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)
