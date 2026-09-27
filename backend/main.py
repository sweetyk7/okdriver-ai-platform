from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import asyncio
import json
import cv2
import os
import threading
from datetime import datetime

import models
import schemas
from database import engine, get_db

from aiortc import RTCPeerConnection, RTCSessionDescription, RTCConfiguration, RTCIceServer
from webrtc_stream import OpenCVStreamTrack
import uuid

# Create new tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="okDriver AI Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- WEBSOCKET FOR REAL-TIME ALERTS ---
class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# --- CAMERA REGISTRY API ---
@app.post("/cameras/", response_model=schemas.CameraResponse, tags=["Cameras"])
def create_camera(camera: schemas.CameraCreate, db: Session = Depends(get_db)):
    db_camera = models.Camera(**camera.model_dump())
    db.add(db_camera)
    db.commit()
    db.refresh(db_camera)
    return db_camera

@app.get("/cameras/", response_model=list[schemas.CameraResponse], tags=["Cameras"])
def get_cameras(db: Session = Depends(get_db)):
    return db.query(models.Camera).all()

@app.delete("/cameras/{camera_id}", tags=["Cameras"])
def delete_camera(camera_id: str, db: Session = Depends(get_db)):
    db_camera = db.query(models.Camera).filter(models.Camera.camera_id == camera_id).first()
    if not db_camera:
        return {"error": "Camera not found"}
    db.delete(db_camera)
    db.commit()
    return {"message": "Camera deleted successfully"}

async def generate_frames(stream_url):
    # Support RTSP, HTTP, or local USB webcam (like "0")
    try:
        url = int(stream_url) if stream_url.isdigit() else stream_url
    except:
        url = stream_url
        
    cap = cv2.VideoCapture(url)
    try:
        while cap.isOpened():
            success, frame = await asyncio.to_thread(cap.read)
            if not success:
                break
            # Reduce resolution for smoother browser stream if needed
            frame = cv2.resize(frame, (640, 360))
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    finally:
        cap.release()

@app.get("/cameras/{camera_id}/stream", tags=["Cameras"])
def stream_camera(camera_id: str, db: Session = Depends(get_db)):
    db_camera = db.query(models.Camera).filter(models.Camera.camera_id == camera_id).first()
    if not db_camera or not db_camera.stream_url:
        return {"error": "Camera stream not found"}
    
    return StreamingResponse(
        generate_frames(db_camera.stream_url), 
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

# --- WEBRTC ENDPOINT ---
pcs = set()

@app.post("/cameras/{camera_id}/webrtc/offer", tags=["Cameras"])
async def webrtc_offer(camera_id: str, offer: schemas.WebRTCOffer, db: Session = Depends(get_db)):
    db_camera = db.query(models.Camera).filter(models.Camera.camera_id == camera_id).first()
    if not db_camera or not db_camera.stream_url:
        return {"error": "Camera stream not found"}

    pc = RTCPeerConnection(configuration=RTCConfiguration(
        iceServers=[RTCIceServer(urls=["stun:stun.l.google.com:19302"])]
    ))
    pc_id = "PeerConnection(%s)" % uuid.uuid4()
    pcs.add(pc)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        print(f"Connection state is {pc.connectionState}")
        if pc.connectionState == "failed" or pc.connectionState == "closed":
            await pc.close()
            pcs.discard(pc)

    video_track = OpenCVStreamTrack(db_camera.stream_url)
    pc.addTrack(video_track)

    offer_sdp = RTCSessionDescription(sdp=offer.sdp, type=offer.type)
    await pc.setRemoteDescription(offer_sdp)

    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}

# --- STORAGE MANAGER FOR MEDIA ---
MEDIA_ROOT = os.path.join(os.path.dirname(__file__), "media")

def get_storage_path(camera_id, media_type):
    # Generates a path like: media/snapshots/2026-09-27/CAM-1/
    today_str = datetime.now().strftime("%Y-%m-%d")
    path = os.path.join(MEDIA_ROOT, media_type, today_str, camera_id)
    os.makedirs(path, exist_ok=True)
    return path

# --- SNAPSHOT API ---
@app.post("/cameras/{camera_id}/snapshot", tags=["Media"])
def take_snapshot(camera_id: str, db: Session = Depends(get_db)):
    db_camera = db.query(models.Camera).filter(models.Camera.camera_id == camera_id).first()
    if not db_camera or not db_camera.stream_url:
        return {"error": "Camera stream not found"}
        
    try:
        url = int(db_camera.stream_url) if db_camera.stream_url.isdigit() else db_camera.stream_url
    except:
        url = db_camera.stream_url
        
    cap = cv2.VideoCapture(url)
    success, frame = cap.read()
    cap.release()
    
    if not success:
        return {"error": "Failed to read frame from camera"}
        
    dir_path = get_storage_path(camera_id, "snapshots")
    filename = f"snap_{datetime.now().strftime('%H-%M-%S')}.jpg"
    filepath = os.path.join(dir_path, filename)
    
    cv2.imwrite(filepath, frame)
    return {"message": "Snapshot saved to server", "path": filepath}

# --- RECORDING API ---
active_recordings = {}

def record_camera_task(camera_id, stream_url, filepath):
    try:
        url = int(stream_url) if stream_url.isdigit() else stream_url
    except:
        url = stream_url
        
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
    
    while active_recordings.get(camera_id, False):
        success, frame = cap.read()
        if not success:
            break
        out.write(frame)
        
    cap.release()
    out.release()

@app.post("/cameras/{camera_id}/record", tags=["Media"])
def toggle_recording(camera_id: str, action: str, db: Session = Depends(get_db)):
    # action should be "start" or "stop"
    if action == "stop":
        if camera_id in active_recordings:
            active_recordings[camera_id] = False
            return {"message": "Recording stopped"}
        return {"error": "Not currently recording"}
        
    if action == "start":
        if active_recordings.get(camera_id, False):
            return {"error": "Already recording"}
            
        db_camera = db.query(models.Camera).filter(models.Camera.camera_id == camera_id).first()
        if not db_camera or not db_camera.stream_url:
            return {"error": "Camera stream not found"}
            
        dir_path = get_storage_path(camera_id, "recordings")
        filename = f"rec_{datetime.now().strftime('%H-%M-%S')}.mp4"
        filepath = os.path.join(dir_path, filename)
        
        active_recordings[camera_id] = True
        
        # Start recording in a background thread
        t = threading.Thread(target=record_camera_task, args=(camera_id, db_camera.stream_url, filepath))
        t.daemon = True
        t.start()
        
        return {"message": "Recording started on server", "path": filepath}


# --- WATCHLIST API ---
@app.post("/watchlist/", tags=["Watchlist"])
def add_to_watchlist(item: schemas.WatchlistCreate, db: Session = Depends(get_db)):
    db_item = models.Watchlist(**item.model_dump())
    db.add(db_item)
    db.commit()
    return {"message": f"Vehicle {item.vehicle_number} added to watchlist"}


# --- AI DETECTION API (MOCK) ---
@app.post("/detect/", tags=["AI Analytics"])
async def ai_detection(event: schemas.DetectionCreate, db: Session = Depends(get_db)):
    # Check if vehicle is in watchlist
    is_alert = 0
    alert_reason = ""
    match = db.query(models.Watchlist).filter(models.Watchlist.vehicle_number == event.vehicle_number).first()
    
    if match:
        is_alert = 1
        alert_reason = match.reason
        
        # Send Real-Time Alert to Frontend via WebSocket
        alert_data = {
            "type": "ALERT",
            "camera_id": event.camera_id,
            "vehicle_number": event.vehicle_number,
            "reason": alert_reason,
            "timestamp": "Just now"
        }
        await manager.broadcast(json.dumps(alert_data))

    # Save event to DB
    new_event = models.DetectionEvent(
        camera_id=event.camera_id, 
        vehicle_number=event.vehicle_number,
        is_alert=is_alert
    )
    db.add(new_event)
    db.commit()

    return {"status": "Detection received", "is_alert": bool(is_alert)}


# --- GET RECENT ALERTS (for polling fallback) ---
@app.get("/alerts/", tags=["AI Analytics"])
def get_recent_alerts(db: Session = Depends(get_db)):
    events = db.query(models.DetectionEvent).filter(
        models.DetectionEvent.is_alert == 1
    ).order_by(models.DetectionEvent.id.desc()).limit(10).all()
    
    result = []
    for e in events:
        # Get reason from watchlist
        match = db.query(models.Watchlist).filter(
            models.Watchlist.vehicle_number == e.vehicle_number
        ).first()
        result.append({
            "camera_id": e.camera_id,
            "vehicle_number": e.vehicle_number,
            "reason": match.reason if match else "Unknown",
            "timestamp": str(e.timestamp)
        })
    return result


# --- VEHICLE MOVEMENT HISTORY ---
@app.get("/vehicles/{vehicle_number}/history", tags=["AI Analytics"])
def get_vehicle_history(vehicle_number: str, db: Session = Depends(get_db)):
    events = db.query(models.DetectionEvent).filter(
        models.DetectionEvent.vehicle_number == vehicle_number
    ).order_by(models.DetectionEvent.id.asc()).all()
    
    result = []
    for e in events:
        cam = db.query(models.Camera).filter(models.Camera.camera_id == e.camera_id).first()
        if cam:
            result.append({
                "camera_id": e.camera_id,
                "latitude": cam.latitude,
                "longitude": cam.longitude,
                "timestamp": str(e.timestamp)
            })
    return result
