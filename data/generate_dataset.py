"""
Script to generate a synthetic historical flood dataset.
Run this once to create data/flood_dataset.csv
"""

import numpy as np
import pandas as pd
import os

np.random.seed(42)
N = 2000

# ── Realistic environmental parameter distributions ──────────────────────────
# High-rainfall monsoon region baseline (e.g., coastal South Asia)
rainfall     = np.clip(np.random.exponential(scale=30, size=N), 0, 300)  # mm
river_level  = np.clip(1.5 + rainfall * 0.04 + np.random.normal(0, 0.5, N), 0.5, 12.0)  # m
humidity     = np.clip(50 + rainfall * 0.15 + np.random.normal(0, 8, N), 20, 100)  # %
temperature  = np.clip(np.random.normal(28, 5, N), 10, 45)  # °C
wind_speed   = np.clip(np.random.exponential(scale=15, size=N), 0, 100)  # km/h

# ── Flood label: physics-based rule + noise ───────────────────────────────────
#    Flood more likely when: heavy rain + high river + high humidity
flood_score = (
    (rainfall      / 300)  * 0.40 +
    (river_level   / 12.0) * 0.35 +
    (humidity      / 100)  * 0.15 +
    (wind_speed    / 100)  * 0.10
)
noise = np.random.normal(0, 0.05, N)
flood_occurred = ((flood_score + noise) > 0.40).astype(int)

df = pd.DataFrame({
    "rainfall_mm":    np.round(rainfall,    2),
    "river_level_m":  np.round(river_level, 2),
    "humidity_pct":   np.round(humidity,    2),
    "temperature_c":  np.round(temperature, 2),
    "wind_speed_kmh": np.round(wind_speed,  2),
    "flood_occurred": flood_occurred,
})

out_path = os.path.join(os.path.dirname(__file__), "flood_dataset.csv")
df.to_csv(out_path, index=False)
print(f"[✓] Dataset saved → {out_path}")
print(df.describe())
print(f"\nFlood events: {flood_occurred.sum()} / {N}  ({flood_occurred.mean()*100:.1f}%)")
