"""
Database seed script - Gujarat-focused demo data for Smart Policing.
Run once: python seed_v2.py
"""
from app.database import SessionLocal, engine, Base
from app.models.department import Department
from app.models.camera import Camera
from app.models.watchlist import Watchlist, FaceWatchlist
from app.models.detection import DetectionEvent, AIDetection
from app.models.user import User
import datetime
import hashlib

# Recreate all tables
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# --- DEPARTMENTS ---
departments = [
    Department(name="Gujarat Police", code="GP", total_cameras=25, district="Ahmedabad"),
    Department(name="Gujarat Traffic Police", code="GTP", total_cameras=20, district="Ahmedabad"),
    Department(name="GSRTC", code="GSRTC", total_cameras=8, district="Ahmedabad"),
    Department(name="Municipal Corporation", code="AMC", total_cameras=15, district="Ahmedabad"),
    Department(name="Health Department", code="GHD", total_cameras=5, district="Ahmedabad"),
    Department(name="Panchayat", code="PAN", total_cameras=10, district="Gandhinagar"),
]

for d in departments:
    db.add(d)
db.flush()

# --- CAMERAS (Gujarat locations) ---
cameras = [
    Camera(camera_id="GJ-CAM-001", name="Sabarmati Ashram Gate", department_name="Gujarat Police",
           camera_type="IP", protocol="RTSP", latitude=23.0609, longitude=72.5808, status="Online",
           zone="Zone 1 - Ahmedabad Central", district="Ahmedabad", health_score=100),
    Camera(camera_id="GJ-CAM-002", name="CG Road Junction", department_name="Gujarat Traffic Police",
           camera_type="PTZ", protocol="RTSP", latitude=23.0225, longitude=72.5714, status="Online",
           zone="Zone 1 - Ahmedabad Central", district="Ahmedabad", health_score=100),
    Camera(camera_id="GJ-CAM-003", name="SG Highway Toll Plaza", department_name="Gujarat Traffic Police",
           camera_type="IP", protocol="RTSP", latitude=23.0469, longitude=72.5142, status="Online",
           zone="Zone 2 - Ahmedabad West", district="Ahmedabad", health_score=95),
    Camera(camera_id="GJ-CAM-004", name="Manek Chowk Market", department_name="Municipal Corporation",
           camera_type="IP", protocol="MJPEG", latitude=23.0257, longitude=72.5856, status="Online",
           zone="Zone 1 - Ahmedabad Central", district="Ahmedabad", health_score=100),
    Camera(camera_id="GJ-CAM-005", name="Kankaria Lake Entrance", department_name="Municipal Corporation",
           camera_type="PTZ", protocol="ONVIF", latitude=23.0068, longitude=72.5995, status="Degraded",
           zone="Zone 3 - Ahmedabad South", district="Ahmedabad", health_score=45),
    Camera(camera_id="GJ-CAM-006", name="GSRTC Bus Terminal Ahmedabad", department_name="GSRTC",
           camera_type="IP", protocol="RTSP", latitude=23.0279, longitude=72.6054, status="Online",
           zone="Zone 1 - Ahmedabad Central", district="Ahmedabad", health_score=100),
    Camera(camera_id="GJ-CAM-007", name="Civil Hospital Gate", department_name="Health Department",
           camera_type="IP", protocol="HTTP", latitude=23.0551, longitude=72.6059, status="Online",
           zone="Zone 1 - Ahmedabad Central", district="Ahmedabad", health_score=88),
    Camera(camera_id="GJ-CAM-008", name="Gandhinagar Sachivalay", department_name="Gujarat Police",
           camera_type="PTZ", protocol="RTSP", latitude=23.2156, longitude=72.6369, status="Online",
           zone="Zone 4 - Gandhinagar", district="Gandhinagar", health_score=100),
    Camera(camera_id="GJ-CAM-009", name="Surat Diamond Bourse Gate", department_name="Gujarat Police",
           camera_type="IP", protocol="RTSP", latitude=21.1421, longitude=72.7709, status="Online",
           zone="Zone 5 - Surat", district="Surat", health_score=100),
    Camera(camera_id="GJ-CAM-010", name="Rajkot Trikon Baug Circle", department_name="Gujarat Traffic Police",
           camera_type="IP", protocol="RTSP", latitude=22.3039, longitude=70.8022, status="Offline",
           zone="Zone 6 - Rajkot", district="Rajkot", health_score=0),
    Camera(camera_id="GJ-CAM-011", name="Vadodara Sayaji Garden Gate", department_name="Municipal Corporation",
           camera_type="IP", protocol="RTSP", latitude=22.3168, longitude=73.1919, status="Online",
           zone="Zone 7 - Vadodara", district="Vadodara", health_score=92),
    Camera(camera_id="GJ-CAM-012", name="Ahmedabad Railway Station", department_name="Gujarat Police",
           camera_type="IP", protocol="RTSP", latitude=23.0268, longitude=72.6006, status="Online",
           zone="Zone 1 - Ahmedabad Central", district="Ahmedabad", health_score=100),
]

for cam in cameras:
    db.add(cam)

# --- WATCHLIST VEHICLES ---
watchlist = [
    Watchlist(vehicle_number="GJ01AB7821", reason="Stolen vehicle - Sabarmati area", severity="Critical", district="Ahmedabad"),
    Watchlist(vehicle_number="GJ05XY3390", reason="Wanted in hit and run - Ring Road", severity="High", district="Surat"),
    Watchlist(vehicle_number="GJ03PQ5541", reason="Involved in robbery - Rajkot", severity="High", district="Rajkot"),
    Watchlist(vehicle_number="GJ06MN2288", reason="Suspected drug transport", severity="Critical", district="Vadodara"),
    Watchlist(vehicle_number="GJ01CD9900", reason="Kidnapping suspect vehicle", severity="Critical", district="Ahmedabad"),
]

for item in watchlist:
    db.add(item)

# --- FACE WATCHLIST ---
faces = [
    FaceWatchlist(person_name="Unknown Suspect #1", reason="Wanted in burglary series - Ahmedabad", severity="High"),
    FaceWatchlist(person_name="Unknown Suspect #2", reason="Missing person alert - Surat", severity="Medium"),
]

for f in faces:
    db.add(f)

# --- DETECTION EVENTS (route history demo) ---
events = [
    DetectionEvent(camera_id="GJ-CAM-001", vehicle_number="GJ01AB7821", is_alert=1,
                   timestamp=datetime.datetime.now() - datetime.timedelta(minutes=60)),
    DetectionEvent(camera_id="GJ-CAM-002", vehicle_number="GJ01AB7821", is_alert=1,
                   timestamp=datetime.datetime.now() - datetime.timedelta(minutes=45)),
    DetectionEvent(camera_id="GJ-CAM-003", vehicle_number="GJ01AB7821", is_alert=1,
                   timestamp=datetime.datetime.now() - datetime.timedelta(minutes=30)),
    DetectionEvent(camera_id="GJ-CAM-006", vehicle_number="GJ01AB7821", is_alert=1,
                   timestamp=datetime.datetime.now() - datetime.timedelta(minutes=15)),
    DetectionEvent(camera_id="GJ-CAM-004", vehicle_number="GJ05XY3390", is_alert=1,
                   timestamp=datetime.datetime.now() - datetime.timedelta(minutes=20)),
]

for event in events:
    db.add(event)

# --- AI DETECTIONS ---
ai_events = [
    AIDetection(camera_id="GJ-CAM-001", detection_type="ANPR", confidence=0.94,
                detected_value="GJ01AB7821", is_alert=1,
                timestamp=datetime.datetime.now() - datetime.timedelta(minutes=60)),
    AIDetection(camera_id="GJ-CAM-002", detection_type="FACE", confidence=0.87,
                detected_value="Unknown Suspect #1", is_alert=1,
                timestamp=datetime.datetime.now() - datetime.timedelta(minutes=50)),
    AIDetection(camera_id="GJ-CAM-005", detection_type="ANOMALY", confidence=0.72,
                detected_value="crowd_gathering", is_alert=0,
                timestamp=datetime.datetime.now() - datetime.timedelta(minutes=40)),
    AIDetection(camera_id="GJ-CAM-003", detection_type="ANPR", confidence=0.91,
                detected_value="GJ03PQ5541", is_alert=1,
                timestamp=datetime.datetime.now() - datetime.timedelta(minutes=25)),
]

for ai in ai_events:
    db.add(ai)

# --- ADMIN USER ---
admin = User(
    username="admin",
    hashed_password=hashlib.sha256("admin123".encode()).hexdigest(),
    full_name="System Administrator",
    role="admin"
)
db.add(admin)

operator = User(
    username="officer1",
    hashed_password=hashlib.sha256("officer123".encode()).hexdigest(),
    full_name="Inspector Rajesh Patel",
    role="operator"
)
db.add(operator)

db.commit()
db.close()

print("=" * 60)
print("  okDriver AI Platform v2.0 - Database Seeded!")
print("=" * 60)
print(f"  {len(departments)} departments added")
print(f"  {len(cameras)} cameras added (across Gujarat)")
print(f"  {len(watchlist)} watchlist vehicles added")
print(f"  {len(faces)} face watchlist entries added")
print(f"  {len(events)} detection events added")
print(f"  {len(ai_events)} AI detection events added")
print(f"  2 users created (admin/admin123, officer1/officer123)")
print("=" * 60)
