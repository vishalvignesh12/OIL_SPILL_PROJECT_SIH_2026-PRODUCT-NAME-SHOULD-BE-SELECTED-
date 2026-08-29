import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Float, ForeignKey, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

class AttributionScore(Base):
    __tablename__ = "attribution_scores"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False)
    vessel_id = Column(UUID(as_uuid=True), ForeignKey("vessels.id", ondelete="CASCADE"), nullable=False)
    score = Column(Float, nullable=False) # combined score [0, 1]
    proximity_score = Column(Float, nullable=False) # spatial [0, 1]
    temporality_score = Column(Float, nullable=False) # temporal [0, 1]
    trajectory_score = Column(Float, nullable=False) # trajectory parity [0, 1]
    anomaly_score = Column(Float, nullable=False) # AIS gap [0, 1]
    anomaly_flag = Column(Boolean, nullable=False, default=False)
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
