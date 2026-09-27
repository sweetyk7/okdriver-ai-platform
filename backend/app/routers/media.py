"""
Media Router - Browse and manage snapshots and recordings.
"""
from fastapi import APIRouter
from app.services.storage import list_recordings, list_snapshots

router = APIRouter()


@router.get("/recordings")
def get_recordings(camera_id: str = None, date: str = None):
    """List all saved recordings, optionally filtered by camera and date."""
    return list_recordings(camera_id=camera_id, date_str=date)


@router.get("/snapshots")
def get_snapshots(camera_id: str = None, date: str = None):
    """List all saved snapshots, optionally filtered by camera and date."""
    return list_snapshots(camera_id=camera_id, date_str=date)
