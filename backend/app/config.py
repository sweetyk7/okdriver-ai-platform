import os
from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./okdriver.db")

# JWT Auth
SECRET_KEY = os.getenv("SECRET_KEY", "okdriver-super-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Media Storage
MEDIA_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "media")

# AI Models
AI_CONFIDENCE_THRESHOLD = 0.5
ANPR_ENABLED = True
FACE_DETECTION_ENABLED = True
ANOMALY_DETECTION_ENABLED = True

# Camera Health Check Interval (seconds)
HEALTH_CHECK_INTERVAL = 30

# Stream Settings
STREAM_RESOLUTION = (640, 360)
STREAM_QUALITY = 80  # JPEG quality 0-100
