"""
okDriver AI Platform - Main Application Factory
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.routers import cameras, watchlist, detection, analytics, media, auth, gov_databases
from app.services.alert_manager import alert_manager
from app.database import engine, Base
from app import models  # noqa: F401 - ensures all models are registered


def create_app() -> FastAPI:
    app = FastAPI(
        title="okDriver AI Platform",
        description="AI-Powered CCTV Monitoring & Smart Policing Platform for Gujarat Police",
        version="2.0.0"
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Create all database tables
    Base.metadata.create_all(bind=engine)

    # Register routers
    app.include_router(auth.router, prefix="/auth", tags=["Auth"])
    app.include_router(cameras.router, prefix="/cameras", tags=["Cameras"])
    app.include_router(watchlist.router, prefix="/watchlist", tags=["Watchlist"])
    app.include_router(detection.router, prefix="/detect", tags=["AI Detection"])
    app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
    app.include_router(media.router, prefix="/media", tags=["Media"])
    app.include_router(gov_databases.router, prefix="/gov", tags=["Government DBs"])

    # Legacy endpoints for backward compatibility with existing frontend
    @app.get("/alerts/")
    def legacy_alerts():
        from app.database import SessionLocal
        db = SessionLocal()
        try:
            from app.models.detection import DetectionEvent
            from app.models.watchlist import Watchlist
            events = db.query(DetectionEvent).filter(
                DetectionEvent.is_alert == 1
            ).order_by(DetectionEvent.id.desc()).limit(10).all()
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
        finally:
            db.close()

    @app.get("/vehicles/{vehicle_number}/history")
    def legacy_vehicle_history(vehicle_number: str):
        from app.database import SessionLocal
        db = SessionLocal()
        try:
            from app.models.detection import DetectionEvent
            from app.models.camera import Camera
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
        finally:
            db.close()

    # WebSocket endpoint for real-time alerts
    @app.websocket("/ws/alerts")
    async def websocket_endpoint(ws: WebSocket):
        await alert_manager.connect(ws)
        try:
            while True:
                await ws.receive_text()
        except WebSocketDisconnect:
            alert_manager.disconnect(ws)

    @app.get("/")
    def root():
        return {
            "name": "okDriver AI Platform",
            "version": "2.0.0",
            "docs": "/docs",
            "status": "running"
        }

    return app


app = create_app()
