import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Float
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

class Vessel(Base):
    __tablename__ = "vessels"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mmsi = Column(String, unique=True, nullable=False, index=True)
    imo = Column(String, nullable=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=True) # Tanker, Cargo, Passenger, etc.
    flag = Column(String, nullable=True) # Flag state (e.g. Panama, India)
    length = Column(Float, nullable=True) # Length in meters
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
