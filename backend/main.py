"""
backend/main.py — FastAPI application for flood risk prediction.

Start with:
    cd d:\\Flood_Prediction_system
    uvicorn backend.main:app --reload --port 8000
"""

import os
import sys
import numpy as np
import joblib
from datetime import datetime, timezone
from typing import Optional, List

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# ── Path setup so we can import sibling modules ───────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from backend.database import init_db, get_db, Prediction
from backend.weather   import fetch_weather, weather_description, DEFAULT_LAT, DEFAULT_LON

# ── Model paths ───────────────────────────────────────────────────────────────
MODEL_PATH  = os.path.join(BASE_DIR, "models", "flood_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "models", "scaler.pkl")

# ── Load ML artefacts at startup ──────────────────────────────────────────────
def _load_model():
    if not os.path.exists(MODEL_PATH):
        raise RuntimeError(
            "Model not found! Run `python train_model.py` first."
        )
    clf    = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    return clf, scaler

clf, scaler = _load_model()

# ── FastAPI application ───────────────────────────────────────────────────────
app = FastAPI(
    title="🌊 Flood Prediction API",
    description="Real-time flood risk prediction using Machine Learning and Open-Meteo weather data.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
# ── Static Frontend ────────────────────────────────────────────────────────
# Check if frontend folder exists (avoids error if only backend is pushed)
frontend_dir = os.path.join(BASE_DIR, "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.on_event("startup")
def startup_event():
    init_db()
    print("[✓] Database initialised.")
    print("[✓] ML model loaded — flood prediction ready.")


# ── Pydantic schemas ──────────────────────────────────────────────────────────
class PredictionResponse(BaseModel):
    timestamp:       str
    location:        str
    latitude:        float
    longitude:       float
    rainfall_mm:     float
    river_level_m:   float
    humidity_pct:    float
    temperature_c:   float
    wind_speed_kmh:  float
    weather_desc:    str
    risk_level:      str          # "HIGH" | "LOW"
    risk_probability: float       # 0.0 – 1.0
    message:         str

class PredictionRecord(BaseModel):
    id:               int
    timestamp:        str
    location:         str
    latitude:         Optional[float]
    longitude:        Optional[float]
    rainfall_mm:      float
    river_level_m:    float
    humidity_pct:     float
    temperature_c:    float
    wind_speed_kmh:   float
    risk_level:       str
    risk_probability: float

    class Config:
        from_attributes = True


# ── Helper: run prediction ──────────────────────────────────────────────────
def _predict(weather: dict) -> tuple[str, float]:
    features = np.array([[
        weather["rainfall_mm"],
        weather["river_level_m"],
        weather["humidity_pct"],
        weather["temperature_c"],
        weather["wind_speed_kmh"],
    ]])
    scaled  = scaler.transform(features)
    proba   = clf.predict_proba(scaled)[0]
    risk_p  = float(proba[1])            # probability of flood=1
    risk    = "HIGH" if risk_p >= 0.50 else "LOW"
    return risk, round(risk_p, 4)


def _save_prediction(db: Session, weather: dict, risk: str, prob: float,
                     lat: float, lon: float, location: str) -> Prediction:
    record = Prediction(
        timestamp      = datetime.now(timezone.utc),
        location       = location,
        latitude       = lat,
        longitude      = lon,
        rainfall_mm    = weather["rainfall_mm"],
        river_level_m  = weather["river_level_m"],
        humidity_pct   = weather["humidity_pct"],
        temperature_c  = weather["temperature_c"],
        wind_speed_kmh = weather["wind_speed_kmh"],
        risk_level     = risk,
        risk_probability = prob,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
def serve_home():
    """Serve the premium integrated dashboard."""
    html_path = os.path.join(BASE_DIR, "frontend", "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return {
        "status":  "online",
        "service": "Flood Prediction API",
        "message": "Frontend not found, but API is live."
    }


@app.get("/health", tags=["Health"])
def health():
    return {
        "status":  "online",
        "service": "Flood Prediction API",
        "version": "1.1.0",
    }


@app.get("/predict", response_model=PredictionResponse, tags=["Prediction"])
def predict_default(db: Session = Depends(get_db)):
    """
    Fetch live weather for default location (Chennai, India)
    and return a flood risk prediction.
    """
    return _predict_for_location(DEFAULT_LAT, DEFAULT_LON, "Chennai, India", db)


@app.get("/predict/{lat}/{lon}", response_model=PredictionResponse, tags=["Prediction"])
def predict_custom(lat: float, lon: float,
                   location: str = Query(default="Custom Location"),
                   db: Session = Depends(get_db)):
    """
    Fetch live weather for custom coordinates and return flood risk prediction.
    """
    return _predict_for_location(lat, lon, location, db)


def _predict_for_location(lat: float, lon: float, location: str,
                           db: Session) -> dict:
    weather = fetch_weather(lat, lon)
    if weather is None:
        raise HTTPException(
            status_code=503,
            detail="Weather API unavailable. Check internet connection."
        )

    risk, prob = _predict(weather)
    _save_prediction(db, weather, risk, prob, lat, lon, location)

    if risk == "HIGH":
        msg = ("⚠️  HIGH FLOOD RISK detected. "
               "Authorities advised to issue warnings and prepare evacuation.")
    else:
        msg = "✅  Low flood risk. Conditions are currently stable."

    return {
        "timestamp":       datetime.now(timezone.utc).isoformat(),
        "location":        location,
        "latitude":        lat,
        "longitude":       lon,
        "rainfall_mm":     weather["rainfall_mm"],
        "river_level_m":   weather["river_level_m"],
        "humidity_pct":    weather["humidity_pct"],
        "temperature_c":   weather["temperature_c"],
        "wind_speed_kmh":  weather["wind_speed_kmh"],
        "weather_desc":    weather.get("weather_desc", weather_description(weather.get("weather_code", 0))),
        "risk_level":      risk,
        "risk_probability": prob,
        "message":         msg,
    }


@app.get("/history", response_model=List[PredictionRecord], tags=["History"])
def get_history(limit: int = Query(default=50, ge=1, le=500),
                db: Session = Depends(get_db)):
    """Return the last N prediction records (default 50)."""
    records = (
        db.query(Prediction)
          .order_by(Prediction.id.desc())
          .limit(limit)
          .all()
    )
    return [
        PredictionRecord(
            id=r.id,
            timestamp=r.timestamp.isoformat() if r.timestamp else "",
            location=r.location or "",
            latitude=r.latitude,
            longitude=r.longitude,
            rainfall_mm=r.rainfall_mm,
            river_level_m=r.river_level_m,
            humidity_pct=r.humidity_pct,
            temperature_c=r.temperature_c,
            wind_speed_kmh=r.wind_speed_kmh,
            risk_level=r.risk_level,
            risk_probability=r.risk_probability,
        )
        for r in records
    ]


@app.delete("/history", tags=["History"])
def clear_history(db: Session = Depends(get_db)):
    """Delete all stored predictions."""
    deleted = db.query(Prediction).delete()
    db.commit()
    return {"message": f"Deleted {deleted} records."}
