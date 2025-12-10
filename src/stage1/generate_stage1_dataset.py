"""
generate_stage1_dataset.py

Generates a 24-hour Stage-1 dataset for the Jaspur (20-Jul-2017) cloudburst event.
Outputs CSV: data/stage1_real_dataset.csv (2880 rows, 30-second cadence)

Columns:
timestamp, temperature, pressure, humidity, rainfall_mm, wind_speed,
pressure_drop_5min, pressure_drop_15min, humidity_change_15min,
cloud_env_pwv, cloud_env_cloud_base, cloud_env_sat_bt, cloud_env_ctc,
cloud_env_radar_dbz, cloud_env_echo_top
"""
import numpy as np
import pandas as pd
import os
from datetime import datetime, timedelta

np.random.seed(42)

# ----- CONFIG -----
# Event metadata (Jaspur 20-Jul-2017) - choose local timezone if needed.
EVENT_DATE = "2017-07-20"
EVENT_PEAK_TIME = "15:00:00"      # approximate peak of rain/core
DURATION_HOURS = 24
FREQ_SECONDS = 30                 # 30-second cadence -> 2880 rows per 24 hours
ROWS_PER_DAY = int(3600 * DURATION_HOURS / FREQ_SECONDS)

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")

OUT_DIR = os.path.abspath(OUT_DIR)
os.makedirs(OUT_DIR, exist_ok=True)
OUT_CSV = os.path.join(OUT_DIR, "stage1_real_dataset.csv")

# ----- time index -----
start_dt = pd.to_datetime(f"{EVENT_DATE} 00:00:00")
time_index = pd.date_range(start=start_dt, periods=ROWS_PER_DAY, freq=f"{FREQ_SECONDS}S")

# Helper: gaussian bump
def gauss(t_index, center, width_seconds, amplitude=1.0):
    # center is a Timestamp
    secs = (t_index - pd.to_datetime(center)).total_seconds()
    sigma = width_seconds
    return amplitude * np.exp(-0.5 * (secs / sigma) ** 2)

# ----- Baselines (approx) -----
# Temperature baseline (°C)
temp_base = 29.0                 # hot summer day baseline
temp_diurnal = 3.5 * np.sin((time_index.hour + time_index.minute/60)/24 * 2*np.pi - 0.5)  # small diurnal
temperature = temp_base + temp_diurnal + np.random.normal(0, 0.25, size=len(time_index))

# Pressure baseline (hPa)
pressure_base = 1008.0 + 0.5 * np.cos((time_index.hour)/24 * 2*np.pi)
pressure = pressure_base + np.random.normal(0, 0.12, size=len(time_index))

# Humidity baseline (%)
humidity_base = 70 + 10 * np.sin((time_index.hour)/24 * 2*np.pi)
humidity = np.clip(humidity_base + np.random.normal(0, 1.5, size=len(time_index)), 30, 100)

# Wind speed baseline (km/h)
wind_speed = np.clip(6 + 2*np.sin((time_index.hour)/6 * 2*np.pi) + np.random.normal(0,0.6,len(time_index)), 0, 40)

# PWV (mm) - use paper value ~ 65 mm for Jaspur event
cloud_env_pwv = np.full(len(time_index), 65.0) + np.random.normal(0, 0.8, size=len(time_index))

# Cloud-base (m) - starts higher then lowers as convection develops
cloud_base = 3000 + 500 * np.sin((time_index.hour)/24 * 2*np.pi) + np.random.normal(0,50,len(time_index))

# Satellite BT (brightness temperature °C) - higher numbers = warmer; we will use Kelvin-like magnitude but expressed as °C for convenience
sat_bt_base = 290 + 1.5 * np.cos((time_index.hour)/24 * 2*np.pi) + np.random.normal(0,0.3,len(time_index))

# Cloud-top cooling rate (CTC degC per 30s) - will be mostly small, spike negative (cooling) prior to event
ctc = np.zeros(len(time_index))

# Radar DBZ baseline (dBZ)
radar_dbz = np.full(len(time_index), 10.0) + np.random.normal(0, 1.2, size=len(time_index))
echo_top = np.full(len(time_index), 4000.0) + np.random.normal(0,50,len(time_index))   # m

# Rainfall baseline (mm per 30s) -> mostly 0 until event
rainfall = np.zeros(len(time_index))

# ----- Event bump parameters -----
# Center = event peak time
event_center = pd.to_datetime(f"{EVENT_DATE} {EVENT_PEAK_TIME}")

# Rainfall: shape to emulate the paper's heavy burst (peak ~136 mm/hr)
# Convert mm/hr -> mm per 30s: mm_per_30s = mm_per_hour / 120
peak_mm_hr = 136.0
peak_mm_30s = peak_mm_hr / 120.0

rain_bump = gauss(time_index, event_center, width_seconds=30*20, amplitude=peak_mm_30s)  # ~20*30s = 10 min sigma
# Add a longer precuror rise
precursor = gauss(time_index, event_center - pd.Timedelta(minutes=30), width_seconds=30*60, amplitude=peak_mm_30s*0.15)

rainfall += rain_bump + precursor
# add some small random drops elsewhere
rainfall += np.random.exponential(0.0005, size=len(time_index))

# Radar DBZ bump: approximate dBZ growth
dbz_bump = gauss(time_index, event_center, width_seconds=30*12, amplitude=45.0)  # add up to 45 dBZ at peak
# But we need baseline + bump (but keep within realistic ranges)
radar_dbz = np.clip(radar_dbz + dbz_bump + np.random.normal(0,0.8,len(time_index)), -10, 70)

# Echo-top growth (m)
echo_top += gauss(time_index, event_center, width_seconds=30*30, amplitude=9000.0)  # up to 9000m extra → 13k
echo_top = np.clip(echo_top, 500, 16000)

# Cloud-base lowering as storm matures (m)
cloud_base = cloud_base - 800 * gauss(time_index, event_center - pd.Timedelta(minutes=10), width_seconds=30*40, amplitude=1.0)
cloud_base = np.clip(cloud_base, 200, 8000)

# Satellite BT (cooling) — drop (cooler) at cloud-top during development (expressed in Kelvin-like)
sat_bt_series = sat_bt_base - 8.0 * gauss(time_index, event_center, width_seconds=30*20, amplitude=1.0)
# CTC (cooling rate) approximate: change in temp per 30s (negative when cooling)
ctc = np.gradient(sat_bt_series)  # degrees per 30s (approx)
# make stronger negative cooling near peak
ctc -= 0.4 * gauss(time_index, event_center, width_seconds=30*10, amplitude=1.0)

# PWV small increase pre-event
cloud_env_pwv += 2.5 * gauss(time_index, event_center - pd.Timedelta(minutes=20), width_seconds=30*60, amplitude=1.0)

# humidity ramp-up tied to rain bump
humidity += 20.0 * gauss(time_index, event_center - pd.Timedelta(minutes=5), width_seconds=30*40, amplitude=1.0)
humidity = np.clip(humidity, 10, 100)

# Temperature drop near event (cooling)
temperature -= 2.5 * gauss(time_index, event_center - pd.Timedelta(minutes=3), width_seconds=30*40, amplitude=1.0)

# Pressure drop: a longer slow fall then a rapid last-5-minute fall
pressure -= 3.5 * gauss(time_index, event_center - pd.Timedelta(minutes=20), width_seconds=30*90, amplitude=1.0)  # slow fall
pressure -= 1.2 * gauss(time_index, event_center - pd.Timedelta(minutes=2), width_seconds=30*5, amplitude=1.0)   # rapid final plunge
pressure = np.round(pressure, 3)

# 5-min and 15-min derived features
# compute rolling differences using pandas (we need timedelta windows in index units)
df_tmp = pd.DataFrame(index=time_index)
df_tmp["pressure"] = pressure
df_tmp["humidity"] = humidity

# Convert window seconds to periods for 30s freq
def diff_minutes(series, minutes):
    window_secs = minutes * 60
    periods = int(window_secs / FREQ_SECONDS)
    if periods < 1:
        periods = 1
    return series.values - series.shift(periods=periods).fillna(method="bfill").values

pressure_drop_5min = diff_minutes(df_tmp["pressure"], 5)
pressure_drop_15min = diff_minutes(df_tmp["pressure"], 15)
humidity_change_15min = diff_minutes(df_tmp["humidity"], 15)

# Assemble DataFrame
df = pd.DataFrame({
    "timestamp": time_index.strftime("%d-%m-%Y %H:%M:%S"),
    "temperature": np.round(temperature, 3),
    "pressure": df_tmp["pressure"].values,
    "humidity": np.round(humidity, 3),
    "rainfall_mm": np.round(rainfall, 4),           # mm per 30s
    "wind_speed": np.round(wind_speed, 3),
    "pressure_drop_5min": np.round(pressure_drop_5min, 3),
    "pressure_drop_15min": np.round(pressure_drop_15min, 3),
    "humidity_change_15min": np.round(humidity_change_15min, 3),
    "cloud_env_pwv": np.round(cloud_env_pwv, 3),
    "cloud_env_cloud_base": np.round(cloud_base, 1),
    "cloud_env_sat_bt": np.round(sat_bt_series, 3),
    "cloud_env_ctc": np.round(ctc, 5),
    "cloud_env_radar_dbz": np.round(radar_dbz, 3),
    "cloud_env_echo_top": np.round(echo_top, 1),
})

# sanity: ensure numeric types
for c in df.columns:
    if c != "timestamp":
        df[c] = pd.to_numeric(df[c], errors="coerce")

# Save
df.to_csv(OUT_CSV, index=False)
print(f"[DONE] Wrote {len(df)} rows to -> {OUT_CSV}")
print("Sample (first 10 rows):")
print(df.head(10).to_string(index=False))
