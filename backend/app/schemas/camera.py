from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CameraCreate(BaseModel):
    camera_id: str
    name: str
    department_name: Optional[str] = "General"
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
    camera_type: str
    protocol: str
    latitude: float
    longitude: float
    status: str
    stream_url: Optional[str] = None
    last_heartbeat: datetime
    health_score: int
    zone: Optional[str] = None
    district: Optional[str] = None

    class Config:
        from_attributes = True


class CameraUpdate(BaseModel):
    name: Optional[str] = None
    stream_url: Optional[str] = None
    status: Optional[str] = None
    zone: Optional[str] = None
    district: Optional[str] = None
