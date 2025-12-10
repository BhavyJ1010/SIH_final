# multi_node_live_generator.py
# Multi-node live generator with rolling features, auto triggers, manual override that affects generator.
# Uses REAL-TIME timestamps while replaying Stage-1 cloud env via index mapping.

import os
import time
import json
import random
from datetime import datetime
from collections import deque

import pandas as pd
import numpy as np

# -------------------------
# Paths / config
# -------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

STAGE1_CSV = os.path.join(DATA_DIR, "stage1_real_dataset.csv")
HARDWARE_CSV = os.path.join(DATA_DIR, "hardware_node0.csv")
LIVE_CSV = os.path.join(DATA_DIR, "live.csv")

MANUAL_STAGE_FILE = os.path.join(DATA_DIR, "manual_stage.json")  
STAGE_STATE_FILE  = os.path.join(DATA_DIR, "stage_state.json")

INTERVAL_SEC = 30
NUM_NODES = 5
MAX_ROWS = 2880 * NUM_NODES

NODES = [
    {"node_id": "node0", "lat": 30.2000, "lon": 78.0000, "hardware": True},
    {"node_id": "node1", "lat": 30.2050, "lon": 78.0050, "hardware": False},
    {"node_id": "node2", "lat": 30.2100, "lon": 78.0100, "hardware": False},
    {"node_id": "node3", "lat": 30.1950, "lon": 77.9950, "hardware": False},
    {"node_id": "node4", "lat": 30.2150, "lon": 78.0150, "hardware": False},
]

NEIGHBOR_PERTURB_SCALE = {
    "temperature": 0.02, "pressure": 0.001, "humidity": 0.03,
    "rainfall_mm": 0.15, "wind_speed": 0.10, "cloud_env_radar_dbz": 0.05
}

FORCE_OFFSETS = {}
FORCE_JITTER = 0.1

WINDOW_5MIN = 5 * 60
WINDOW_15MIN = 15 * 60

TRIG_DBZ_STAGE2 = 45.0
TRIG_PRESSURE_DROP_5 = -2.0
TRIG_HUMIDITY_RISE_15 = 8.0
TRIG_DBZ_GROWTH_STAGE3 = 6.0

# -------------------------
# Load Stage-1 cloud env replay
# -------------------------
if not os.path.exists(STAGE1_CSV):
    raise FileNotFoundError("Stage-1 dataset missing! Run generator first.")

stage1_df = pd.read_csv(STAGE1_CSV, parse_dates=["timestamp"], dayfirst=True)
stage1_df = stage1_df.sort_values("timestamp").reset_index(drop=True)

TOTAL_TIMESTEPS = len(stage1_df)

# -------------------------
# Rolling history per node
# -------------------------
SLOTS_15MIN = int(WINDOW_15MIN / INTERVAL_SEC) + 2
node_history = {
    n["node_id"]: {
        "pressure": deque(maxlen=SLOTS_15MIN),
        "humidity": deque(maxlen=SLOTS_15MIN),
        "timestamps": deque(maxlen=SLOTS_15MIN)
    }
    for n in NODES
}

# -------------------------
# Stage-state persistence
# -------------------------
def load_stage_state():
    if os.path.exists(STAGE_STATE_FILE):
        try:
            return json.load(open(STAGE_STATE_FILE))
        except:
            pass
    return {n["node_id"]: 1 for n in NODES}

def save_stage_state(x):
    json.dump(x, open(STAGE_STATE_FILE, "w"), indent=2)

stage_state = load_stage_state()

# -------------------------
# Manual override loader
# -------------------------
def load_manual_override():
    if not os.path.exists(MANUAL_STAGE_FILE):
        return {}
    try:
        d = json.load(open(MANUAL_STAGE_FILE))
        if isinstance(d, dict):
            # normalize ints
            return {k: int(v) for k, v in d.items()}
    except:
        pass
    return {}

# -------------------------
# Hardware / noise utils
# -------------------------
def read_latest_hardware_row():
    if not os.path.exists(HARDWARE_CSV):
        return None
    try:
        df = pd.read_csv(HARDWARE_CSV)
        if df.empty:
            return None
        row = df.iloc[-1]
        return {
            "temperature": float(row.get("temperature", np.nan)),
            "pressure": float(row.get("pressure", np.nan)),
            "humidity": float(row.get("humidity", np.nan)),
            "rainfall_mm": float(row.get("rainfall_mm", np.nan)),
            "wind_speed": float(row.get("wind_speed", np.nan)),
        }
    except:
        return None

def perturb(val, key):
    if key not in NEIGHBOR_PERTURB_SCALE:
        return val
    scale = NEIGHBOR_PERTURB_SCALE[key]
    return val * (1 + random.gauss(0, scale))

def apply_force(val, key):
    if key not in FORCE_OFFSETS:
        return val
    return val + FORCE_OFFSETS[key] + random.gauss(0, FORCE_JITTER)

# -------------------------
# Stage-2 & Stage-3 synthetic microphysics
# -------------------------
state2 = {n["node_id"]: {} for n in NODES}
state3 = {n["node_id"]: {} for n in NODES}

def synth_stage2(n, jump=False, manual_force=False):
    S = state2[n]
    def g(k, base, noise, jf=2):
        old = S.get(k, base)
        if jump or manual_force:
            new = old + random.uniform(noise * jf, noise * jf * 3)
        else:
            new = old + random.uniform(-noise, noise)
        S[k] = new
        return round(new, 4)
    return {
        "micro_lwc": g("lwc",0.5,0.2),
        "micro_droplet_size": g("drop",1.0,0.1),
        "micro_vertical_wind": g("vwind",3.0,0.5),
        "micro_turbulence": g("turb",1.0,0.3),
        "micro_moisture_gradient": g("mgrad",4.0,0.5),
        "micro_temp_gradient": g("tgrad",1.5,0.3),
    }

def synth_stage3(n, jump=False, manual_force=False):
    S = state3[n]
    def g(k, base, noise, jf=3):
        old = S.get(k, base)
        if jump or manual_force:
            new = old + random.uniform(noise * jf, noise * jf * 4)
        else:
            new = old + random.uniform(-noise, noise)
        S[k] = new
        return round(new, 4)
    return {
        "burst_dbz_growth": g("dbg",2.0,1.0),
        "burst_updraft_surge": g("up",6.0,2.0),
        "burst_lightning_burst": int(max(0,g("lbatk",3.0,1.5))),
        "burst_lwc_spike": g("lsp",1.0,0.6),
        "burst_drop_collapse": g("dcol",0.5,0.2),
        "burst_rainfall_burst": g("rburst",5.0,1.5),
    }

# -------------------------
# Rolling differences
# -------------------------
def compute_rolling(nid):
    h = node_history[nid]
    if len(h["pressure"]) < 2:
        return (0.0, 0.0, 0.0)
    curr_p = h["pressure"][-1]
    curr_h = h["humidity"][-1]

    def nth(dq, i):
        if len(dq) <= i:
            return dq[0]
        return dq[-1 - i]

    slots5 = int(WINDOW_5MIN / INTERVAL_SEC)
    slots15 = int(WINDOW_15MIN / INTERVAL_SEC)

    p5 = nth(h["pressure"], slots5)
    p15 = nth(h["pressure"], slots15)
    h15 = nth(h["humidity"], slots15)

    return (
        round(curr_p - p5, 4),
        round(curr_p - p15, 4),
        round(curr_h - h15, 4),
    )

# -------------------------
# Automatic trigger evaluation
# -------------------------
def evaluate_auto_trigger(nid, base, rolling):
    pd5, pd15, h15 = rolling
    dbz = float(base.get("cloud_env_radar_dbz", 0.0))

    stage2 = (dbz >= TRIG_DBZ_STAGE2) or (pd5 <= TRIG_PRESSURE_DROP_5 and h15 >= TRIG_HUMIDITY_RISE_15)

    stage3 = False
    if stage_state.get(nid, 1) >= 2:
        dbg = float(base.get("burst_dbz_growth", 0.0))
        if dbg >= TRIG_DBZ_GROWTH_STAGE3:
            stage3 = True

    return stage2, stage3

# -------------------------
# Persistence with rotation
# -------------------------
def append_rotate(df_new):
    if os.path.exists(LIVE_CSV):
        try:
            old = pd.read_csv(LIVE_CSV)
        except:
            old = pd.DataFrame()
    else:
        old = pd.DataFrame()

    df = pd.concat([old, df_new], ignore_index=True)
    if len(df) > MAX_ROWS:
        df = df.iloc[-MAX_ROWS:]
    df.to_csv(LIVE_CSV, index=False)

# -------------------------
# Main loop
# -------------------------
def run(loop_forever=True):
    print("[START] REAL-TIME multi-node generator running... (manual override affects generator)")

    idx = 0
    while True:
        ts = datetime.now()

        # Use modulo to replay cloud-env realistically without timestamps
        replay_row = stage1_df.iloc[idx % TOTAL_TIMESTEPS].to_dict()

        hw = read_latest_hardware_row()
        manual_map = load_manual_override()
        rows = []

        for node in NODES:
            nid = node["node_id"]

            # Surface metrics (hardware or replay)
            if node["hardware"] and hw:
                temp = hw["temperature"]
                pres = hw["pressure"]
                hum  = hw["humidity"]
                rain = hw["rainfall_mm"]
                wspd = hw["wind_speed"]
            else:
                temp = replay_row.get("temperature", 25.0)
                pres  = replay_row.get("pressure", 1010.0)
                hum   = replay_row.get("humidity", 60.0)
                rain  = replay_row.get("rainfall_mm", 0.0)
                wspd  = replay_row.get("wind_speed", 3.0)

                # neighbor perturb
                temp = perturb(temp, "temperature")
                pres  = perturb(pres, "pressure")
                hum   = perturb(hum, "humidity")
                rain  = max(0, perturb(rain, "rainfall_mm"))
                wspd  = max(0, perturb(wspd, "wind_speed"))

            # force offsets
            temp = apply_force(temp, "temperature")
            pres  = apply_force(pres, "pressure")
            hum   = apply_force(hum, "humidity")
            rain  = apply_force(rain, "rainfall_mm")

            # update history
            hist = node_history[nid]
            hist["pressure"].append(float(pres))
            hist["humidity"].append(float(hum))
            hist["timestamps"].append(ts)

            # rolling diffs
            pd5, pd15, hum15 = compute_rolling(nid)

            # stage decision (manual overrides now affect generator)
            manual_mode = False
            if nid in manual_map and manual_map[nid] in (1,2,3):
                stage_now = int(manual_map[nid])
                manual_mode = True
            else:
                stage_now = stage_state.get(nid, 1)
                auto2, auto3 = evaluate_auto_trigger(nid, replay_row, (pd5, pd15, hum15))
                if stage_now == 1 and auto2:
                    stage_now = 2
                if stage_now == 2 and auto3:
                    stage_now = 3

            # persist stage
            stage_state[nid] = stage_now

            # generate synthetic microphysics; stronger jumps when manual forced
            s2 = synth_stage2(nid, jump=(stage_now >= 2), manual_force=manual_mode)
            s3 = synth_stage3(nid, jump=(stage_now >= 3), manual_force=manual_mode)

            # build row
            row = {
                "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
                "node_id": nid, "lat": node["lat"], "lon": node["lon"],
                "temperature": round(temp,4), "pressure": round(pres,4), "humidity": round(hum,4),
                "rainfall_mm": round(rain,6), "wind_speed": round(wspd,4),
                "pressure_drop_5": pd5, "pressure_drop_15": pd15, "humidity_change_15": hum15,
                "stage": stage_now
            }

            # cloud env from replay_row (spatially same for nodes; perturb if needed)
            for k in ["cloud_env_pwv","cloud_env_cloud_base","cloud_env_radar_dbz","cloud_env_echo_top",
                      "cloud_env_lightning","cloud_env_sat_bt","cloud_env_ctc","cloud_env_moisture_column",
                      "cloud_env_convective_index"]:
                # neighbor perturb small for selected keys (to get multi-node diversity)
                val = replay_row.get(k, 0)
                if k in ("cloud_env_radar_dbz","cloud_env_echo_top"):
                    val = perturb(val, "cloud_env_radar_dbz")
                row[k] = val

            # micro + burst fields
            row.update(s2)
            row.update(s3)

            # risk_score: simple placeholder (we'll regenerate training data later for ML)
            if manual_mode:
                # when manual override, push risk higher (reflect operator concern)
                risk = random.uniform(60, 98) if stage_now >= 2 else random.uniform(10,30)
            else:
                risk = random.uniform(0, 40) if stage_now == 1 else random.uniform(30, 85) if stage_now == 2 else random.uniform(70, 100)
            row["risk_score"] = round(risk, 3)

            # notes
            if manual_mode:
                row["notes"] = f"manual_override:{manual_map[nid]}"
            else:
                row["notes"] = ""

            rows.append(row)

        # save stage_state & append to live.csv
        save_stage_state(stage_state)
        df_out = pd.DataFrame(rows)
        append_rotate(df_out)

        # simple log (time only to keep output compact)
        print(f"[{ts.strftime('%Y-%m-%d %H:%M:%S')}] wrote {len(rows)} rows | stages={stage_state}")

        idx += 1
        time.sleep(INTERVAL_SEC)

if __name__ == "__main__":
    run()
