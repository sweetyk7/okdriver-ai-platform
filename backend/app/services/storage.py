"""
Storage Manager - Handles server-side media file storage.
Organizes snapshots and recordings in a scalable folder hierarchy:
  media/<type>/<date>/<camera_id>/<filename>
"""
import os
from datetime import datetime
from app.config import MEDIA_ROOT


def get_storage_path(camera_id: str, media_type: str) -> str:
    """
    Generate and create a structured storage path.
    Example: media/snapshots/2026-09-27/CAM-1/
    """
    today_str = datetime.now().strftime("%Y-%m-%d")
    path = os.path.join(MEDIA_ROOT, media_type, today_str, camera_id)
    os.makedirs(path, exist_ok=True)
    return path


def generate_filename(prefix: str, extension: str) -> str:
    """Generate a timestamped filename. Example: snap_16-08-30.jpg"""
    return f"{prefix}_{datetime.now().strftime('%H-%M-%S')}.{extension}"


def list_recordings(camera_id: str = None, date_str: str = None):
    """List all recordings, optionally filtered by camera and date."""
    recordings = []
    recordings_root = os.path.join(MEDIA_ROOT, "recordings")

    if not os.path.exists(recordings_root):
        return recordings

    for date_dir in sorted(os.listdir(recordings_root), reverse=True):
        if date_str and date_dir != date_str:
            continue
        date_path = os.path.join(recordings_root, date_dir)
        if not os.path.isdir(date_path):
            continue
        for cam_dir in os.listdir(date_path):
            if camera_id and cam_dir != camera_id:
                continue
            cam_path = os.path.join(date_path, cam_dir)
            if not os.path.isdir(cam_path):
                continue
            for filename in os.listdir(cam_path):
                filepath = os.path.join(cam_path, filename)
                recordings.append({
                    "camera_id": cam_dir,
                    "date": date_dir,
                    "filename": filename,
                    "path": filepath,
                    "size_mb": round(os.path.getsize(filepath) / (1024 * 1024), 2)
                })

    return recordings


def list_snapshots(camera_id: str = None, date_str: str = None):
    """List all snapshots, optionally filtered by camera and date."""
    snapshots = []
    snapshots_root = os.path.join(MEDIA_ROOT, "snapshots")

    if not os.path.exists(snapshots_root):
        return snapshots

    for date_dir in sorted(os.listdir(snapshots_root), reverse=True):
        if date_str and date_dir != date_str:
            continue
        date_path = os.path.join(snapshots_root, date_dir)
        if not os.path.isdir(date_path):
            continue
        for cam_dir in os.listdir(date_path):
            if camera_id and cam_dir != camera_id:
                continue
            cam_path = os.path.join(date_path, cam_dir)
            if not os.path.isdir(cam_path):
                continue
            for filename in os.listdir(cam_path):
                filepath = os.path.join(cam_path, filename)
                snapshots.append({
                    "camera_id": cam_dir,
                    "date": date_dir,
                    "filename": filename,
                    "path": filepath,
                    "size_kb": round(os.path.getsize(filepath) / 1024, 2)
                })

    return snapshots
