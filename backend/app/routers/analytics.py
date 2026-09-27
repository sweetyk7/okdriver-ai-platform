"""
Analytics Router - Statistics, charts data, and system overview.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.camera import Camera
from app.models.detection import DetectionEvent, AIDetection
from app.models.watchlist import Watchlist, FaceWatchlist

router = APIRouter()


@router.get("/overview")
def get_overview(db: Session = Depends(get_db)):
    """Get full system overview for the dashboard."""
    return {
        "cameras": {
            "total": db.query(Camera).count(),
            "online": db.query(Camera).filter(Camera.status == "Online").count(),
            "offline": db.query(Camera).filter(Camera.status == "Offline").count(),
            "degraded": db.query(Camera).filter(Camera.status == "Degraded").count(),
        },
        "watchlist": {
            "vehicles": db.query(Watchlist).count(),
            "faces": db.query(FaceWatchlist).count(),
        },
        "detections": {
            "total_events": db.query(DetectionEvent).count(),
            "total_alerts": db.query(DetectionEvent).filter(DetectionEvent.is_alert == 1).count(),
            "ai_detections": db.query(AIDetection).count(),
        }
    }


@router.get("/detections-by-type")
def detections_by_type(db: Session = Depends(get_db)):
    """Chart data: Detection counts grouped by type."""
    results = db.query(
        AIDetection.detection_type, func.count(AIDetection.id)
    ).group_by(AIDetection.detection_type).all()

    return [{"type": t, "count": c} for t, c in results]


@router.get("/detections-by-camera")
def detections_by_camera(limit: int = 10, db: Session = Depends(get_db)):
    """Chart data: Top cameras by detection count."""
    results = db.query(
        DetectionEvent.camera_id, func.count(DetectionEvent.id)
    ).group_by(DetectionEvent.camera_id).order_by(
        func.count(DetectionEvent.id).desc()
    ).limit(limit).all()

    return [{"camera_id": cam, "count": c} for cam, c in results]


@router.get("/alerts-by-hour")
def alerts_by_hour(db: Session = Depends(get_db)):
    """Chart data: Alert counts by hour of day."""
    events = db.query(DetectionEvent).filter(DetectionEvent.is_alert == 1).all()
    hour_counts = {}
    for e in events:
        if e.timestamp:
            h = e.timestamp.hour
            hour_counts[h] = hour_counts.get(h, 0) + 1
    return [{"hour": h, "count": c} for h, c in sorted(hour_counts.items())]


@router.get("/camera-health")
def camera_health_summary(db: Session = Depends(get_db)):
    """Chart data: Camera health distribution."""
    cameras = db.query(Camera).all()
    healthy = sum(1 for c in cameras if c.health_score >= 80)
    warning = sum(1 for c in cameras if 40 <= c.health_score < 80)
    critical = sum(1 for c in cameras if c.health_score < 40)
    return [
        {"status": "Healthy", "count": healthy},
        {"status": "Warning", "count": warning},
        {"status": "Critical", "count": critical},
    ]
