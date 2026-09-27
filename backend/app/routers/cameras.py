"""
Camera Router - CRUD, streaming, health, snapshot, recording.
"""
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import cv2
import os
import threading

from app.database import get_db
from app.models.camera import Camera
from app.schemas.camera import CameraCreate, CameraResponse, CameraUpdate
from app.services.stream_manager import generate_frames, capture_single_frame
from app.services.storage import get_storage_path, generate_filename

router = APIRouter()

# --- CRUD ---

@router.post("/", response_model=CameraResponse)
def create_camera(camera: CameraCreate, db: Session = Depends(get_db)):
    db_camera = Camera(**camera.model_dump())
    db.add(db_camera)
    db.commit()
    db.refresh(db_camera)
    return db_camera


@router.get("/", response_model=list[CameraResponse])
def get_cameras(
    skip: int = 0,
    limit: int = 100,
    department: str = None,
    status: str = None,
    zone: str = None,
    district: str = None,
    search: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(Camera)
    if department:
        query = query.filter(Camera.department_name == department)
    if status:
        query = query.filter(Camera.status == status)
    if zone:
        query = query.filter(Camera.zone == zone)
    if district:
        query = query.filter(Camera.district == district)
    if search:
        query = query.filter(
            (Camera.camera_id.contains(search)) | (Camera.name.contains(search))
        )
    return query.offset(skip).limit(limit).all()


@router.get("/stats")
def get_camera_stats(db: Session = Depends(get_db)):
    total = db.query(Camera).count()
    online = db.query(Camera).filter(Camera.status == "Online").count()
    offline = db.query(Camera).filter(Camera.status == "Offline").count()
    degraded = db.query(Camera).filter(Camera.status == "Degraded").count()
    return {
        "total": total,
        "online": online,
        "offline": offline,
        "degraded": degraded,
        "departments": _get_department_counts(db)
    }


def _get_department_counts(db: Session):
    """Get camera counts per department."""
    from sqlalchemy import func
    results = db.query(Camera.department_name, func.count(Camera.id)).group_by(Camera.department_name).all()
    return {dept or "Unknown": count for dept, count in results}


@router.get("/{camera_id}")
def get_camera(camera_id: str, db: Session = Depends(get_db)):
    cam = db.query(Camera).filter(Camera.camera_id == camera_id).first()
    if not cam:
        return {"error": "Camera not found"}
    return cam


@router.put("/{camera_id}")
def update_camera(camera_id: str, update: CameraUpdate, db: Session = Depends(get_db)):
    cam = db.query(Camera).filter(Camera.camera_id == camera_id).first()
    if not cam:
        return {"error": "Camera not found"}
    for key, value in update.model_dump(exclude_unset=True).items():
        setattr(cam, key, value)
    db.commit()
    db.refresh(cam)
    return cam


@router.delete("/{camera_id}")
def delete_camera(camera_id: str, db: Session = Depends(get_db)):
    db_camera = db.query(Camera).filter(Camera.camera_id == camera_id).first()
    if not db_camera:
        return {"error": "Camera not found"}
    db.delete(db_camera)
    db.commit()
    return {"message": "Camera deleted successfully"}


# --- STREAMING ---

@router.get("/{camera_id}/stream")
def stream_camera(camera_id: str, db: Session = Depends(get_db)):
    db_camera = db.query(Camera).filter(Camera.camera_id == camera_id).first()
    if not db_camera or not db_camera.stream_url:
        return {"error": "Camera stream not found"}
    return StreamingResponse(
        generate_frames(db_camera.stream_url),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


# --- SNAPSHOTS ---

@router.post("/{camera_id}/snapshot")
def take_snapshot(camera_id: str, db: Session = Depends(get_db)):
    db_camera = db.query(Camera).filter(Camera.camera_id == camera_id).first()
    if not db_camera or not db_camera.stream_url:
        return {"error": "Camera stream not found"}

    success, frame = capture_single_frame(db_camera.stream_url)
    if not success:
        return {"error": "Failed to read frame from camera"}

    dir_path = get_storage_path(camera_id, "snapshots")
    filename = generate_filename("snap", "jpg")
    filepath = os.path.join(dir_path, filename)

    cv2.imwrite(filepath, frame)
    return {"message": "Snapshot saved to server", "path": filepath}


# --- RECORDING ---

_active_recordings = {}


def _record_task(camera_id, stream_url, filepath):
    from app.services.stream_manager import parse_stream_url
    url = parse_stream_url(stream_url)
    cap = cv2.VideoCapture(url)
    if not cap.isOpened():
        return

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    if not fps or fps <= 0:
        fps = 20.0

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filepath, fourcc, fps, (width, height))

    while _active_recordings.get(camera_id, False):
        success, frame = cap.read()
        if not success:
            break
        out.write(frame)

    cap.release()
    out.release()


@router.post("/{camera_id}/record")
def toggle_recording(camera_id: str, action: str, db: Session = Depends(get_db)):
    if action == "stop":
        if camera_id in _active_recordings:
            _active_recordings[camera_id] = False
            return {"message": "Recording stopped"}
        return {"error": "Not currently recording"}

    if action == "start":
        if _active_recordings.get(camera_id, False):
            return {"error": "Already recording"}

        db_camera = db.query(Camera).filter(Camera.camera_id == camera_id).first()
        if not db_camera or not db_camera.stream_url:
            return {"error": "Camera stream not found"}

        dir_path = get_storage_path(camera_id, "recordings")
        filename = generate_filename("rec", "mp4")
        filepath = os.path.join(dir_path, filename)

        _active_recordings[camera_id] = True
        t = threading.Thread(target=_record_task, args=(camera_id, db_camera.stream_url, filepath))
        t.daemon = True
        t.start()

        return {"message": "Recording started on server", "path": filepath}

    return {"error": "Invalid action. Use 'start' or 'stop'."}
