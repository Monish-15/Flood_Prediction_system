"""
backend/database.py — SQLite database setup and ORM models via SQLAlchemy.
"""

import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if os.environ.get("VERCEL"):
    DB_PATH = "/tmp/flood_predictions.db"
else:
    DB_PATH = os.path.join(BASE_DIR, "..", "flood_predictions.db")

DB_URL = f"sqlite:///{os.path.normpath(DB_PATH)}"

engine       = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base         = declarative_base()


class Prediction(Base):
    """Stores each flood risk prediction result."""
    __tablename__ = "predictions"

    id            = Column(Integer,  primary_key=True, index=True)
    timestamp     = Column(DateTime, default=datetime.utcnow, nullable=False)
    location      = Column(String,   default="Chennai, India")
    latitude      = Column(Float,    nullable=True)
    longitude     = Column(Float,    nullable=True)
    rainfall_mm   = Column(Float,    nullable=False)
    river_level_m = Column(Float,    nullable=False)
    humidity_pct  = Column(Float,    nullable=False)
    temperature_c = Column(Float,    nullable=False)
    wind_speed_kmh= Column(Float,    nullable=False)
    risk_level    = Column(String,   nullable=False)   # "HIGH" | "LOW"
    risk_probability = Column(Float, nullable=False)   # 0.0 – 1.0


def init_db():
    """Create all tables (idempotent)."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency — yields a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
