"""
Watchlist Router - Vehicle + Face watchlist management.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.watchlist import Watchlist, FaceWatchlist
from app.schemas.watchlist import WatchlistCreate, WatchlistResponse, FaceWatchlistCreate

router = APIRouter()


# --- VEHICLE WATCHLIST ---

@router.post("/vehicles")
def add_vehicle(item: WatchlistCreate, db: Session = Depends(get_db)):
    existing = db.query(Watchlist).filter(Watchlist.vehicle_number == item.vehicle_number).first()
    if existing:
        return {"message": f"Vehicle {item.vehicle_number} already in watchlist"}
    db_item = Watchlist(**item.model_dump())
    db.add(db_item)
    db.commit()
    return {"message": f"Vehicle {item.vehicle_number} added to watchlist"}


@router.get("/vehicles", response_model=list[WatchlistResponse])
def get_vehicle_watchlist(
    skip: int = 0, limit: int = 50,
    severity: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(Watchlist)
    if severity:
        query = query.filter(Watchlist.severity == severity)
    return query.offset(skip).limit(limit).all()


@router.delete("/vehicles/{vehicle_number}")
def remove_vehicle(vehicle_number: str, db: Session = Depends(get_db)):
    item = db.query(Watchlist).filter(Watchlist.vehicle_number == vehicle_number).first()
    if not item:
        return {"error": "Vehicle not in watchlist"}
    db.delete(item)
    db.commit()
    return {"message": f"Vehicle {vehicle_number} removed from watchlist"}


@router.get("/vehicles/count")
def vehicle_count(db: Session = Depends(get_db)):
    return {"count": db.query(Watchlist).count()}


# --- FACE WATCHLIST ---

@router.post("/faces")
def add_face(item: FaceWatchlistCreate, db: Session = Depends(get_db)):
    db_item = FaceWatchlist(**item.model_dump())
    db.add(db_item)
    db.commit()
    return {"message": f"Face entry for '{item.person_name}' added to watchlist"}


@router.get("/faces")
def get_face_watchlist(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return db.query(FaceWatchlist).offset(skip).limit(limit).all()


@router.delete("/faces/{face_id}")
def remove_face(face_id: int, db: Session = Depends(get_db)):
    item = db.query(FaceWatchlist).filter(FaceWatchlist.id == face_id).first()
    if not item:
        return {"error": "Face entry not found"}
    db.delete(item)
    db.commit()
    return {"message": "Face entry removed from watchlist"}


# --- LEGACY COMPATIBILITY (for existing frontend) ---

@router.post("/")
def add_vehicle_legacy(item: WatchlistCreate, db: Session = Depends(get_db)):
    """Legacy endpoint: POST /watchlist/ for backward compatibility."""
    return add_vehicle(item, db)
