# generate_synthetic_training.py
# Improved multi-node synthetic training data generator with sharp Stage-1->2->3 transitions.
# Produces realistic correlated features for NUM_DAYS and NUM_NODES.

import os
import random
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

OUT_CSV = os.path.join(DATA_DIR, "training_data.csv")

# Config
NUM_DAYS = 60                 # change if you want more/less data
NUM_NODES = 5
ROWS_PER_DAY = 2880           # 30-sec cadence
TOTAL_ROWS = NUM_DAYS * ROWS_PER_DAY * NUM_NODES

random.seed(42)
np.random.seed(42)

def synth_day_for_node(day_index, node_idx, day_type, event_start_idx):
    """
    day_type: "clean", "stormy", "cloudburst"
    event_start_idx: index within day when convective growth starts (0..ROWS_PER_DAY-1)
    We'll implement SHARP transitions: stage changes within minutes (2-10 minutes).
    """
    rows = []
    # baseline environmental randomization per node/day
    temp_base = 25 + random.uniform(-3, 3)
    pres_base = 1010 + random.uniform(-5, 5)
    hum_base = 55 + random.uniform(-10, 10)
    pwv_base = 45 + random.uniform(-5, 25)

    # Choose exact event start offset per node to simulate spatial lag (± 0-10 intervals)
    node_offset = random.randint(-6, 6)  # ±3 minutes
    start_idx = max(0, min(ROWS_PER_DAY-1, event_start_idx + node_offset))

    # For sharp transitions, stage2 rise period (in intervals) = 4-20 intervals (~2-10 minutes)
    stage2_rise = random.randint(4, 20)
    stage3_rise = random.randint(4, 20)

    # event peak indices
    stage2_onset = start_idx
    stage3_onset = min(ROWS_PER_DAY-1, stage2_onset + stage2_rise + random.randint(6, 40))  # short delay

    for i in range(ROWS_PER_DAY):
        ts = (datetime.now().replace(microsecond=0) + timedelta(seconds=30*i)).strftime("%Y-%m-%d %H:%M:%S")

        # baseline random walk small noise
        temp = temp_base + np.random.normal(0, 0.5)
        pressure = pres_base + np.random.normal(0, 0.3)
        humidity = np.clip(hum_base + np.random.normal(0, 1.5), 10, 100)
        wind_speed = max(0.0, np.random.normal(4.0, 1.0))
        rainfall = max(0.0, np.random.exponential(0.0005))

        # cloud env baseline
        cloud_env_pwv = pwv_base + np.random.normal(0, 0.5)
        cloud_env_radar_dbz = max(0.0, np.random.normal(8.0, 2.0))
        cloud_env_echo_top = max(1000.0, np.random.normal(4000.0, 200.0))
        cloud_env_lightning = 0
        cloud_env_sat_bt = 290 + np.random.normal(0, 0.4)
        cloud_env_ctc = np.random.normal(0, 0.05)

        stage = 1

        # decide stage and apply sharp transitions
        if day_type == "clean":
            # mostly stage1
            stage = 1
            risk = random.uniform(0, 20)
        else:
            # before stage2 onset
            if i < stage2_onset:
                stage = 1
                risk = random.uniform(5, 25)
            # stage2 ramp (sharp)
            elif i < stage2_onset + stage2_rise:
                # linear ramp into stage2
                frac = (i - stage2_onset + 1) / max(1, stage2_rise)
                stage = 2
                # dbz rises quickly
                cloud_env_radar_dbz += 20 * frac + np.random.normal(0, 1.5)
                cloud_env_pwv += 2.0 * frac
                humidity += 8.0 * frac
                pressure -= 1.0 * frac  # small pressure fall
                cloud_env_ctc -= 0.2 * frac
                risk = 30 + 40 * frac + np.random.normal(0, 5)
                cloud_env_lightning = int( np.random.poisson(0.1 + 2*frac) )
            # between stage2 and stage3 onset (brief)
            elif i < stage3_onset:
                stage = 2
                cloud_env_radar_dbz += np.random.normal(25, 5)
                cloud_env_pwv += 2.5
                humidity += 8.0
                pressure -= 1.5
                cloud_env_ctc -= 0.3
                cloud_env_lightning = int(np.random.poisson(1))
                risk = random.uniform(45, 70)
            # stage3 ramp (sharp)
            elif i < stage3_onset + stage3_rise:
                frac = (i - stage3_onset + 1) / max(1, stage3_rise)
                stage = 3
                cloud_env_radar_dbz += 45 * frac + np.random.normal(0, 3.0)
                cloud_env_echo_top += 4000 * frac
                cloud_env_pwv += 4.0 * frac
                humidity += 15.0 * frac
                pressure -= 2.0 * frac  # rapid pressure plunge
                cloud_env_ctc -= 0.6 * frac
                cloud_env_lightning = int(np.random.poisson(3 * frac + 0.5))
                # intense rainfall near peak
                rainfall += (10.0 * frac) / 120.0  # convert mm/hr style to per-30s small magnitude
                risk = 70 + 30 * frac + np.random.normal(0, 5)
            else:
                # after peak - either maintain or collapse
                stage = 3
                cloud_env_radar_dbz += np.random.normal(45, 10)
                cloud_env_echo_top += 2000
                cloud_env_pwv += 3.0
                humidity += 5.0
                pressure -= 1.0
                cloud_env_ctc -= 0.2
                cloud_env_lightning = int(np.random.poisson(2))
                risk = random.uniform(60, 95)

        # microphysics (depend on stage)
        micro_lwc = 0.2 + 0.3 * (stage >= 2) + (0.5 if stage >= 3 else 0.0) + np.random.normal(0, 0.1)
        micro_droplet_size = 1.0 + 0.3 * (stage >= 2) + np.random.normal(0, 0.2)
        micro_vertical_wind = max(0, np.random.normal(2 + 2*(stage>=2) + 3*(stage>=3), 1.0))
        micro_turbulence = max(0, np.random.normal(0.5 + 0.7*(stage>=2) + 1.0*(stage>=3), 0.3))
        micro_moisture_gradient = max(0, np.random.normal(2 + 2*(stage>=2), 0.8))
        micro_temp_gradient = np.random.normal(0.5 + 0.5*(stage>=2), 0.2)

        # burst signals
        burst_dbz_growth = np.random.uniform(0, 2) if stage < 3 else np.random.uniform(6, 15)
        burst_updraft_surge = np.random.uniform(0, 3) if stage < 2 else np.random.uniform(3, 12)
        burst_lightning_burst = int(np.random.poisson(0.1 if stage < 2 else (2 if stage==2 else 6)))
        burst_lwc_spike = np.random.uniform(0, 0.5) if stage < 3 else np.random.uniform(1.0, 4.0)
        burst_drop_collapse = np.random.uniform(0, 0.5) if stage < 3 else np.random.uniform(0.5, 2.5)
        burst_rainfall_burst = np.random.uniform(0, 1.0) if stage < 3 else np.random.uniform(3.0, 20.0)

        row = {
            "timestamp": ts,
            "node_id": f"node{node_idx}",
            "lat": 30.20 + 0.001*node_idx,
            "lon": 78.00 + 0.001*node_idx,
            "temperature": round(temp, 3),
            "pressure": round(pressure, 3),
            "humidity": round(humidity, 3),
            "rainfall_mm": round(rainfall, 6),
            "wind_speed": round(wind_speed, 3),
            "pressure_drop_5": 0.0,           # computed later with rolling
            "pressure_drop_15": 0.0,
            "humidity_change_15": 0.0,
            "cloud_env_pwv": round(cloud_env_pwv, 3),
            "cloud_env_cloud_base": round(max(200, 3000 - (humidity - 40)*10), 1),
            "cloud_env_radar_dbz": round(cloud_env_radar_dbz, 3),
            "cloud_env_lightning": int(cloud_env_lightning),
            "cloud_env_sat_bt": round(cloud_env_sat_bt, 3),
            "cloud_env_ctc": round(cloud_env_ctc, 5),
            "cloud_env_moisture_column": round(cloud_env_pwv/2.0, 3),
            "cloud_env_convective_index": round(max(0.0, (cloud_env_radar_dbz/50.0)), 3),
            # micro + burst
            "micro_lwc": round(micro_lwc, 4),
            "micro_droplet_size": round(micro_droplet_size, 4),
            "micro_vertical_wind": round(micro_vertical_wind, 4),
            "micro_turbulence": round(micro_turbulence, 4),
            "micro_moisture_gradient": round(micro_moisture_gradient, 4),
            "micro_temp_gradient": round(micro_temp_gradient, 4),
            "burst_dbz_growth": round(burst_dbz_growth, 4),
            "burst_updraft_surge": round(burst_updraft_surge, 4),
            "burst_lightning_burst": int(burst_lightning_burst),
            "burst_lwc_spike": round(burst_lwc_spike, 4),
            "burst_drop_collapse": round(burst_drop_collapse, 4),
            "burst_rainfall_burst": round(burst_rainfall_burst, 4),
            "stage": int(stage),
            "risk_score": round(float(np.clip(risk, 0, 100)), 3)
        }

        rows.append(row)
    return rows

def compute_rolling_for_all(df):
    # expects df sorted by node then timestamp, per-node compute pressure drop and humidity change
    df = df.sort_values(["node_id", "timestamp"]).reset_index(drop=True)
    out_rows = []
    grouped = df.groupby("node_id")
    for node, g in grouped:
        g = g.reset_index(drop=True)
        # compute pressure differences using windows of 5min (10 intervals) and 15min (30 intervals)
        g["pressure_drop_5"] = g["pressure"] - g["pressure"].shift(10).fillna(method="bfill")
        g["pressure_drop_15"] = g["pressure"] - g["pressure"].shift(30).fillna(method="bfill")
        g["humidity_change_15"] = g["humidity"] - g["humidity"].shift(30).fillna(method="bfill")
        out_rows.append(g)
    df_out = pd.concat(out_rows, ignore_index=True)
    # ensure numeric types
    for c in ["pressure_drop_5", "pressure_drop_15", "humidity_change_15"]:
        df_out[c] = df_out[c].astype(float).round(4)
    return df_out

def make_dataset(days=NUM_DAYS, nodes=NUM_NODES):
    all_rows = []
    for d in range(days):
        # pick day_type probabilistically (more clean days)
        day_type = random.choices(["clean", "stormy", "cloudburst"], weights=[0.6, 0.3, 0.1])[0]
        # pick event start index (if not clean)
        if day_type == "clean":
            event_start = rows_per_day_index = ROWS_PER_DAY // 2  # unused
        else:
            event_start = random.randint(ROWS_PER_DAY//4, 3*ROWS_PER_DAY//4)
        for n in range(nodes):
            rows = synth_day_for_node(d, n, day_type, event_start)
            all_rows.extend(rows)
    df = pd.DataFrame(all_rows)
    # compute rolling features per node
    df = compute_rolling_for_all(df)
    # shuffle so training has mixed timestamps across nodes/days
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    return df

if __name__ == "__main__":
    print("[START] Generating synthetic training dataset (sharp transitions, multi-node)...")
    df = make_dataset()
    df.to_csv(OUT_CSV, index=False)
    print(f"[DONE] Wrote {len(df)} rows to -> {OUT_CSV}")
