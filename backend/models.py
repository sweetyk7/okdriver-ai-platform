from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base
import datetime

class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(String, unique=True, index=True)
    name = Column(String)
    department_id = Column(Integer, nullable=True)
    department_name = Column(String, nullable=True)
    camera_type = Column(String, default="IP")
    protocol = Column(String, default="RTSP")
    latitude = Column(Float)
    longitude = Column(Float)
    status = Column(String, default="Online")
    stream_url = Column(String, nullable=True)
    last_heartbeat = Column(DateTime, default=datetime.datetime.utcnow)
    health_score = Column(Integer, default=100)
    zone = Column(String, nullable=True)
    district = Column(String, nullable=True)

class Watchlist(Base):
    __tablename__ = "watchlist"
    
    id = Column(Integer, primary_key=True, index=True)
    vehicle_number = Column(String, unique=True, index=True)
    reason = Column(String) # e.g. "Stolen", "Wanted"

class DetectionEvent(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(String)
    vehicle_number = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    is_alert = Column(Integer, default=0) # 1 if matched with watchlist
