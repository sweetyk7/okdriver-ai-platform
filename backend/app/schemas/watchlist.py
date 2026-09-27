from pydantic import BaseModel
from typing import Optional


class WatchlistCreate(BaseModel):
    vehicle_number: str
    reason: str
    severity: Optional[str] = "High"
    district: Optional[str] = None


class WatchlistResponse(BaseModel):
    id: int
    vehicle_number: str
    reason: str
    severity: str
    district: Optional[str] = None

    class Config:
        from_attributes = True


class FaceWatchlistCreate(BaseModel):
    person_name: str
    reason: str
    severity: Optional[str] = "High"
    district: Optional[str] = None


class DetectionCreate(BaseModel):
    camera_id: str
    vehicle_number: str
