import uuid
from datetime import datetime, UTC
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
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)
