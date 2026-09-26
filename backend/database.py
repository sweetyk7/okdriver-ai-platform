from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# Hum SQLite use kar rahe hain (ek file base database) taaki aapko extra software na dalna pade abhi
SQLALCHEMY_DATABASE_URL = "sqlite:///./okdriver.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency database connect karne ke liye
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
