from sqlalchemy import Column, Integer, String
from app.database import Base


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)              # "Gujarat Police", "GSRTC", "Municipal Corp"
    code = Column(String, unique=True)               # "GP", "GSRTC", "MC"
    total_cameras = Column(Integer, default=0)
    contact_officer = Column(String, nullable=True)
    district = Column(String, nullable=True)
