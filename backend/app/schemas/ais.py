from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel

class AISQuery(BaseModel):
    start_time: datetime
    end_time: datetime
    bbox: Optional[str] = None # format: lon_min,lat_min,lon_max,lat_max
    vessel_id: Optional[UUID] = None

class AISGapAlert(BaseModel):
    anomaly_flag: bool = True
    gap_start: datetime
    gap_end: datetime
    priority: str # HIGH, MEDIUM, LOW
    explanation: str
