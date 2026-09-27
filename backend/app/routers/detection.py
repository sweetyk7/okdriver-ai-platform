"""
Detection Router - AI detection events, alerts, vehicle history.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.detection import DetectionEvent, AIDetection
from app.models.watchlist import Watchlist
from app.models.camera import Camera
from app.schemas.watchlist import DetectionCreate
from app.services.alert_manager import alert_manager

router = APIRouter()


@router.post("/")
async def ai_detection(event: DetectionCreate, db: Session = Depends(get_db)):
    """Submit an AI detection event. Auto-checks against watchlist."""
    is_alert = 0
    alert_reason = ""
    match = db.query(Watchlist).filter(Watchlist.vehicle_number == event.vehicle_number).first()

    if match:
        is_alert = 1
        alert_reason = match.reason
        await alert_manager.send_alert(event.camera_id, event.vehicle_number, alert_reason)

    new_event = DetectionEvent(
        camera_id=event.camera_id,
        vehicle_number=event.vehicle_number,
        is_alert=is_alert
    )
    db.add(new_event)
    db.commit()

    return {"status": "Detection received", "is_alert": bool(is_alert)}


@router.get("/alerts")
def get_recent_alerts(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get recent watchlist alerts."""
    events = db.query(DetectionEvent).filter(
        DetectionEvent.is_alert == 1
    ).order_by(DetectionEvent.id.desc()).offset(skip).limit(limit).all()

    result = []
    for e in events:
        match = db.query(Watchlist).filter(
            Watchlist.vehicle_number == e.vehicle_number
        ).first()
        result.append({
            "camera_id": e.camera_id,
            "vehicle_number": e.vehicle_number,
            "reason": match.reason if match else "Unknown",
            "timestamp": str(e.timestamp)
        })
    return result


@router.get("/ai-detections")
def get_ai_detections(
    detection_type: str = None,
    camera_id: str = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get AI detection events with filters."""
    query = db.query(AIDetection)
    if detection_type:
        query = query.filter(AIDetection.detection_type == detection_type)
    if camera_id:
        query = query.filter(AIDetection.camera_id == camera_id)
    return query.order_by(AIDetection.id.desc()).offset(skip).limit(limit).all()


@router.get("/vehicles/{vehicle_number}/history")
def get_vehicle_history(vehicle_number: str, db: Session = Depends(get_db)):
    """Get cross-camera movement history for a vehicle."""
    events = db.query(DetectionEvent).filter(
        DetectionEvent.vehicle_number == vehicle_number
    ).order_by(DetectionEvent.id.asc()).all()

    result = []
    for e in events:
        cam = db.query(Camera).filter(Camera.camera_id == e.camera_id).first()
        if cam:
            result.append({
                "camera_id": e.camera_id,
                "latitude": cam.latitude,
                "longitude": cam.longitude,
                "timestamp": str(e.timestamp)
            })
    return result
