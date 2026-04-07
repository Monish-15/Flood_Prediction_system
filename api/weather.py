import os
import requests
import random
from typing import Optional

# Use environment variable for safety. Set this in Vercel or your local .env
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "YOUR_API_KEY_HERE")
OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

# Default: Coimbatore, India
DEFAULT_LAT = 11.0055
DEFAULT_LON = 76.9661
DEFAULT_LOC = "Coimbatore, India"

def _estimate_river_level(rainfall_mm: float) -> float:
    """
    Heuristic proxy: river level rises ~0.06 m per mm of rainfall
    from a baseline of 1.5 m, capped at 12 m.
    """
    return round(min(1.5 + rainfall_mm * 0.06, 12.0), 2)


def fetch_weather(lat: float = DEFAULT_LAT, lon: float = DEFAULT_LON) -> Optional[dict]:
    """
    Call OpenWeatherMap API and return a clean parameter dict.
    Returns mock data gracefully if the API is unreachable.
    """
    try:
        params = {
            "lat": lat,
            "lon": lon,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric"
        }
        
        resp = requests.get(OPENWEATHER_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        temperature_c = float(data.get("main", {}).get("temp", 28.0))
        humidity_pct = float(data.get("main", {}).get("humidity", 70.0))
        wind_speed_m_s = float(data.get("wind", {}).get("speed", 2.0))
        wind_speed_kmh = wind_speed_m_s * 3.6
        
        # OWM sometimes provides rainfall under 'rain', usually '1h'
        rain_data = data.get("rain", {})
        rainfall_mm = float(rain_data.get("1h", 0.0))
        
        weather_list = data.get("weather", [])
        weather_desc = weather_list[0].get("description", "Unknown") if weather_list else "Unknown"
        weather_code = weather_list[0].get("id", 0) if weather_list else 0
        
        river_level_m = _estimate_river_level(rainfall_mm)
        
        return {
            "rainfall_mm": round(rainfall_mm, 1),
            "river_level_m": river_level_m,
            "humidity_pct": round(humidity_pct, 1),
            "temperature_c": round(temperature_c, 1),
            "wind_speed_kmh": round(wind_speed_kmh, 1),
            "weather_code": weather_code,
            "weather_desc": weather_desc.title(),
            "timezone": "UTC"
        }
    except Exception as exc:
        print(f"[weather] API error: {exc}. Using mock fallback data.")
        rainfall_mm = random.uniform(0.0, 50.0)
        return {
            "rainfall_mm": round(rainfall_mm, 1),
            "river_level_m": _estimate_river_level(rainfall_mm),
            "humidity_pct": round(random.uniform(60.0, 95.0), 1),
            "temperature_c": round(random.uniform(20.0, 35.0), 1),
            "wind_speed_kmh": round(random.uniform(5.0, 30.0), 1),
            "weather_code": 800,
            "weather_desc": "Clear Sky mock fallback",
            "timezone": "UTC",
        }


def weather_description(code: int) -> str:
    """WMO weather interpretation code → human-readable string.
    Note: OpenWeatherMap returns string descriptions directly, so this isn't strictly needed anymore,
    but we keep it for fallback/interface compatibility if called directly.
    """
    return "Weather Info"
