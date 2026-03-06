"""
backend/weather.py — Fetch real-time weather data from the Open-Meteo API.
"""

import requests
from typing import Optional

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# Default: Chennai, India — coastal, flood-prone city
DEFAULT_LAT = 13.0827
DEFAULT_LON = 80.2707
DEFAULT_LOC = "Chennai, India"

# Rough estimate: river level proxy from accumulated rainfall
# In a real system this would come from a river gauge sensor.
def _estimate_river_level(rainfall_mm: float) -> float:
    """
    Heuristic proxy: river level rises ~0.06 m per mm of rainfall
    from a baseline of 1.5 m, capped at 12 m.
    """
    return round(min(1.5 + rainfall_mm * 0.06, 12.0), 2)


def fetch_weather(lat: float = DEFAULT_LAT,
                  lon: float = DEFAULT_LON) -> Optional[dict]:
    """
    Call Open-Meteo API and return a clean parameter dict.

    Returns None if the API is unreachable (caller should handle gracefully).
    """
    params = {
        "latitude":   lat,
        "longitude":  lon,
        "current":    [
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
            "wind_speed_10m",
            "weather_code",
        ],
        "hourly":     "precipitation",
        "forecast_days": 1,
        "timezone":   "auto",
    }

    try:
        resp = requests.get(OPEN_METEO_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as exc:
        print(f"[weather] API error: {exc}")
        return None

    current = data.get("current", {})

    rainfall_mm    = float(current.get("precipitation", 0.0))
    temperature_c  = float(current.get("temperature_2m", 28.0))
    humidity_pct   = float(current.get("relative_humidity_2m", 70.0))
    wind_speed_kmh = float(current.get("wind_speed_10m", 10.0))
    weather_code   = int(current.get("weather_code", 0))
    river_level_m  = _estimate_river_level(rainfall_mm)

    return {
        "rainfall_mm":    rainfall_mm,
        "river_level_m":  river_level_m,
        "humidity_pct":   humidity_pct,
        "temperature_c":  temperature_c,
        "wind_speed_kmh": wind_speed_kmh,
        "weather_code":   weather_code,
        "timezone":       data.get("timezone", "UTC"),
    }


def weather_description(code: int) -> str:
    """WMO weather interpretation code → human-readable string."""
    table = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Foggy", 48: "Depositing rime fog",
        51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
        61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
        80: "Slight showers", 81: "Moderate showers", 82: "Violent showers",
        95: "Thunderstorm", 96: "Thunderstorm with hail",
        99: "Thunderstorm with heavy hail",
    }
    return table.get(code, f"Code {code}")
