from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any

# Schemas for the Investigation entity (new feature)
class InvestigationEntityBase(BaseModel):
    title: str = Field(..., example="Suspected Oil Spill — Arabian Sea")
    description: Optional[str] = Field(None, example="Investigation initiated from satellite detection")
    priority: str = Field(..., example="HIGH")

class InvestigationEntityCreate(InvestigationEntityBase):
    detection_id: UUID = Field(..., example="123e4567-e89b-12d3-a456-426614174000")

class InvestigationEntityUpdate(BaseModel):
    title: Optional[str] = Field(None, example="Updated Investigation Title")
    description: Optional[str] = Field(None, example="Updated analyst notes")
    priority: Optional[str] = Field(None, example="CRITICAL")

class InvestigationEntityResponse(InvestigationEntityBase):
    id: UUID
    detection_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Schemas for the aggregated investigation details (existing dashboard)
class InvestigationAggregatedResponse(BaseModel):
    incident: Optional[Dict[str, Any]] = None
    slick: Optional[Dict[str, Any]] = None
    drift: Optional[Dict[str, Any]] = None
    vessels: List[Dict[str, Any]] = []
    attribution: List[Dict[str, Any]] = []
    ais_alerts: List[Dict[str, Any]] = []
    evidence: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

# Investigation Event schemas
class InvestigationEventBase(BaseModel):
    event_type: str = Field(..., example="INVESTIGATION_CREATED")
    message: str = Field(..., example="Investigation created")
    event_metadata: Optional[Dict[str, Any]] = Field(None, example={"key": "value"})

class InvestigationEventCreate(InvestigationEventBase):
    investigation_id: UUID

class InvestigationEventResponse(InvestigationEventBase):
    id: UUID
    investigation_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True