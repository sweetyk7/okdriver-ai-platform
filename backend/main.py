from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import asyncio
import json

import models
import schemas
from database import engine, get_db

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
