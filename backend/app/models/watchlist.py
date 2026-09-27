from sqlalchemy import Column, Integer, String
from app.database import Base


class Watchlist(Base):
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_number = Column(String, unique=True, index=True)
    reason = Column(String)           # e.g. "Stolen", "Wanted"
    severity = Column(String, default="High")  # "Critical", "High", "Medium", "Low"
    added_by = Column(String, nullable=True)
    district = Column(String, nullable=True)


class FaceWatchlist(Base):
    __tablename__ = "face_watchlist"

    id = Column(Integer, primary_key=True, index=True)
    person_name = Column(String)
    reason = Column(String)
    severity = Column(String, default="High")
    face_encoding_path = Column(String, nullable=True)  # Path to stored face encoding
    photo_path = Column(String, nullable=True)
    added_by = Column(String, nullable=True)
    district = Column(String, nullable=True)
