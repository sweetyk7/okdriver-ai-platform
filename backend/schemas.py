from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CameraCreate(BaseModel):
    camera_id: str
    name: str
    department: str
    latitude: float
    longitude: float
    stream_url: Optional[str] = None

class CameraResponse(BaseModel):
    id: int
    camera_id: str
    name: str
    department: str
    latitude: float
    longitude: float
    status: str
    stream_url: Optional[str] = None
    last_heartbeat: datetime

    class Config:
        from_attributes = True

class WatchlistCreate(BaseModel):
    vehicle_number: str
    reason: str

class DetectionCreate(BaseModel):
    camera_id: str
    vehicle_number: str
