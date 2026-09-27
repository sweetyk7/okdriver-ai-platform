"""
Alert Manager - WebSocket connection management and broadcast.
"""
from fastapi import WebSocket, WebSocketDisconnect
import json


class AlertManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """Broadcast a message dict to all connected WebSocket clients."""
        msg_str = json.dumps(message)
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(msg_str)
            except:
                disconnected.append(connection)
        # Clean up dead connections
        for conn in disconnected:
            self.disconnect(conn)

    async def send_alert(self, camera_id: str, vehicle_number: str, reason: str, detection_type: str = "ANPR"):
        """Send a structured alert to all connected clients."""
        alert = {
            "type": "ALERT",
            "detection_type": detection_type,
            "camera_id": camera_id,
            "vehicle_number": vehicle_number,
            "reason": reason,
            "timestamp": "Just now"
        }
        await self.broadcast(alert)


# Singleton instance
alert_manager = AlertManager()
