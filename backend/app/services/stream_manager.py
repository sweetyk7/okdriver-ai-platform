"""
Stream Manager - Handles OpenCV camera connections.
Manages connection pools, frame generation, and stream health.
"""
import cv2
from app.config import STREAM_RESOLUTION, STREAM_QUALITY


import asyncio

def parse_stream_url(stream_url):
    """Convert stream URL string to appropriate type for OpenCV."""
    try:
        return int(stream_url) if stream_url.isdigit() else stream_url
    except:
        return stream_url


async def generate_frames(stream_url):
    """
    Async generator that yields MJPEG frames from any camera source.
    Supports: RTSP, HTTP/MJPEG, USB webcam (index as string like "0").
    """
    url = parse_stream_url(stream_url)
    cap = cv2.VideoCapture(url)

    try:
        while cap.isOpened():
            success, frame = await asyncio.to_thread(cap.read)
            if not success:
                break
            frame = cv2.resize(frame, STREAM_RESOLUTION)
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, STREAM_QUALITY])
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    finally:
        cap.release()


def capture_single_frame(stream_url):
    """Capture a single frame from a camera. Returns (success, frame)."""
    url = parse_stream_url(stream_url)
    cap = cv2.VideoCapture(url)
    try:
        success, frame = cap.read()
    finally:
        cap.release()
    return success, frame


def check_stream_health(stream_url):
    """Check if a camera stream is reachable. Returns health_score (0-100)."""
    url = parse_stream_url(stream_url)
    try:
        cap = cv2.VideoCapture(url)
        try:
            if cap.isOpened():
                success, _ = cap.read()
                return 100 if success else 50
            return 0
        finally:
            cap.release()
    except Exception:
        return 0
