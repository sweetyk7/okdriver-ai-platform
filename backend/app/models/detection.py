from sqlalchemy import Column, Integer, String, Float, DateTime
from app.database import Base
import datetime


class DetectionEvent(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(String, index=True)
    vehicle_number = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    is_alert = Column(Integer, default=0)  # 1 if matched with watchlist


class AIDetection(Base):
    __tablename__ = "ai_detections"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(String, index=True)
    detection_type = Column(String, index=True)     # "ANPR", "FACE", "ANOMALY", "CROWD"
    confidence = Column(Float)
    detected_value = Column(String)                  # plate number, face ID, anomaly type
    snapshot_path = Column(String, nullable=True)
    matched_watchlist_id = Column(Integer, nullable=True)
    is_alert = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    metadata_json = Column(String, nullable=True)    # Extra data as JSON string
