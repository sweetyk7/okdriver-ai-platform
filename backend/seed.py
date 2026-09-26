"""
Database seed script - Delhi specific data
Run once to populate fresh data
"""
from database import SessionLocal, engine
import models
import datetime

# Create all tables fresh
models.Base.metadata.drop_all(bind=engine)
models.Base.metadata.create_all(bind=engine)

db = SessionLocal()

# --- ADD DELHI CAMERAS ---
cameras = [
    models.Camera(camera_id="DL-CAM-01", name="Sarojini Nagar Chowk", department="Delhi Traffic Police", latitude=28.5745, longitude=77.1975, status="Online"),
    models.Camera(camera_id="DL-CAM-02", name="India Gate Circle", department="Delhi Traffic Police", latitude=28.6129, longitude=77.2295, status="Online"),
    models.Camera(camera_id="DL-CAM-03", name="Gurudwara Bangla Sahib Road", department="Delhi Police", latitude=28.6257, longitude=77.2100, status="Online"),
    models.Camera(camera_id="DL-CAM-04", name="Connaught Place Entry", department="Delhi Police", latitude=28.6315, longitude=77.2167, status="Online"),
    models.Camera(camera_id="DL-CAM-05", name="Lajpat Nagar Market Gate", department="Delhi Traffic Police", latitude=28.5676, longitude=77.2432, status="Degraded"),
]

for cam in cameras:
    db.add(cam)

# --- ADD WATCHLIST VEHICLES ---
watchlist = [
    models.Watchlist(vehicle_number="DL-4C-AB-7821", reason="Stolen vehicle reported in Lajpat Nagar"),
    models.Watchlist(vehicle_number="DL-8S-XY-3390", reason="Wanted in hit and run case"),
    models.Watchlist(vehicle_number="DL-1C-PQ-5541", reason="Involved in robbery - Karol Bagh"),
]

for item in watchlist:
    db.add(item)

# --- ADD SAMPLE DETECTION EVENTS (shows route history) ---
events = [
    models.DetectionEvent(camera_id="DL-CAM-01", vehicle_number="DL-4C-AB-7821", is_alert=1, timestamp=datetime.datetime.now() - datetime.timedelta(minutes=30)),
    models.DetectionEvent(camera_id="DL-CAM-02", vehicle_number="DL-4C-AB-7821", is_alert=1, timestamp=datetime.datetime.now() - datetime.timedelta(minutes=20)),
    models.DetectionEvent(camera_id="DL-CAM-03", vehicle_number="DL-4C-AB-7821", is_alert=1, timestamp=datetime.datetime.now() - datetime.timedelta(minutes=10)),
]

for event in events:
    db.add(event)

db.commit()
db.close()

print("Database seeded successfully with Delhi data!")
print("5 cameras added")
print("3 watchlist vehicles added")
print("3 detection events added (for route history demo)")
