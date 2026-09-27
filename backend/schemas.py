from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CameraCreate(BaseModel):
    camera_id: str
    name: str
    department_name: Optional[str] = None
    camera_type: Optional[str] = "IP"
    protocol: Optional[str] = "RTSP"
    latitude: float
    longitude: float
    stream_url: Optional[str] = None
    zone: Optional[str] = None
    district: Optional[str] = None

class CameraResponse(BaseModel):
    id: int
    camera_id: str
    name: str
    department_name: Optional[str] = None
    camera_type: Optional[str] = None
    protocol: Optional[str] = None
    latitude: float
    longitude: float
    status: str
    stream_url: Optional[str] = None
    last_heartbeat: datetime
    health_score: Optional[int] = None
    zone: Optional[str] = None
    district: Optional[str] = None

    class Config:
        from_attributes = True

class WatchlistCreate(BaseModel):
    vehicle_number: str
    reason: str

class DetectionCreate(BaseModel):
    camera_id: str
    vehicle_number: str

class WebRTCOffer(BaseModel):
    sdp: str
    type: str
