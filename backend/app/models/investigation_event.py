import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class InvestigationEvent(Base):
    __tablename__ = "investigation_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    investigation_id = Column(UUID(as_uuid=True), ForeignKey("investigations.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String, nullable=False)  # We can use Enum later if needed, but String is fine for now
    message = Column(Text, nullable=False)
    event_metadata = Column(Text, nullable=True)  # Storing JSON as Text, or we could use JSON type if preferred
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    # created_by can be added later if authentication is available

    # Relationship to Investigation
    investigation = relationship("Investigation", back_populates="events")