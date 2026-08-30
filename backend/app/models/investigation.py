import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
from enum import Enum as PyEnum

class InvestigationStatus(PyEnum):
    OPEN = "OPEN"
    ANALYZING = "ANALYZING"
    REVIEW = "REVIEW"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"

class InvestigationPriority(PyEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class Investigation(Base):
    __tablename__ = "investigations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    detection_id = Column(UUID(as_uuid=True), ForeignKey("slick_detections.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    status = Column(Enum(InvestigationStatus), nullable=False, default=InvestigationStatus.OPEN)
    priority = Column(Enum(InvestigationPriority), nullable=False, default=InvestigationPriority.LOW)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    # created_by can be added later if authentication is available
    # created_by = Column(UUID(as_uuid=True), nullable=True)

    # Relationship to SlickDetection
    detection = relationship("SlickDetection", back_populates="investigation")
    # Relationship to InvestigationEvent
    events = relationship("InvestigationEvent", back_populates="investigation", cascade="all, delete-orphan")

# We need to add the relationship in SlickDetection as well, but we'll do that later by editing slick_detection.py