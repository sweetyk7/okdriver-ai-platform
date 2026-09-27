from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import datetime


class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(String, unique=True, index=True)
    name = Column(String)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    department_name = Column(String, nullable=True)  # Denormalized for quick access
    camera_type = Column(String, default="IP")       # "IP", "Analog", "PTZ", "Mobile"
    protocol = Column(String, default="RTSP")        # "RTSP", "MJPEG", "ONVIF", "HTTP"
    latitude = Column(Float)
    longitude = Column(Float)
    status = Column(String, default="Online")        # "Online", "Offline", "Degraded"
    stream_url = Column(String, nullable=True)
    last_heartbeat = Column(DateTime, default=datetime.datetime.utcnow)
    health_score = Column(Integer, default=100)      # 0-100
    zone = Column(String, nullable=True)             # "Zone 1 - Ahmedabad", etc.
    district = Column(String, nullable=True)
