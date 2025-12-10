# realtime_predictor_continuous.py
# Stable continuous predictor using generator stage + real-time timestamps
# Stores last 10 prediction blocks

import os
import json
import time
from pathlib import Path
from datetime import datetime
import joblib
import pandas as pd
import numpy as np
from hardware_output_writer import write_hardware_output


BASE = Path(__file__).resolve().parents[2]
DATA_DIR = BASE / "data"
MODELS_DIR = BASE / "models"

LIVE_CSV = DATA_DIR / "live.csv"
MANUAL_STAGE_FILE = DATA_DIR / "manual_stage.json"
PRED_OUT = DATA_DIR / "prediction.json"
PREPROC_FILE = MODELS_DIR / "preprocessing.joblib"

STG1_MODEL = MODELS_DIR / "stage1_model.pkl"
STG2_MODEL = MODELS_DIR / "stage2_model.pkl"
STG3_MODEL = MODELS_DIR / "stage3_model.pkl"


# ---------------------------
# JSON-safe conversion
# ---------------------------
def json_safe(x):
    if isinstance(x, (np.int64, np.int32, np.integer)):
        return int(x)
    if isinstance(x, (np.float64, np.float32, np.floating)):
        return float(x)
    if isinstance(x, dict):
        return {k: json_safe(v) for k,v in x.items()}
    if isinstance(x, list):
        return [json_safe(v) for v in x]
    return x


# ---------------------------
# Load models
# ---------------------------
def load_models():
    pre = joblib.load(PREPROC_FILE)
    imputer = pre["imputer"]
    feature_cols = pre["feature_cols"]

    stage_models = {
        1: joblib.load(STG1_MODEL) if STG1_MODEL.exists() else None,
        2: joblib.load(STG2_MODEL) if STG2_MODEL.exists() else None,
        3: joblib.load(STG3_MODEL) if STG3_MODEL.exists() else None
    }

    return imputer, feature_cols, stage_models


# ---------------------------
# Read live data
# ---------------------------
def read_latest_rows():
    if not LIVE_CSV.exists():
        return None
    df = pd.read_csv(LIVE_CSV)
    if df.empty:
        return None
    last_ts = df["timestamp"].iloc[-1]
    return df[df["timestamp"] == last_ts].copy()


# ---------------------------
# Manual stage override
# ---------------------------
def load_manual_stage():
    if not MANUAL_STAGE_FILE.exists():
        return {}
    try:
        return {k:int(v) for k,v in json.loads(MANUAL_STAGE_FILE.read_text()).items()}
    except:
        return {}


# ---------------------------
# Predict risk using regressor only
# ---------------------------
def predict_risk(row, stage_models, imputer, feature_cols):
    stage = int(row["stage"])
    model = stage_models.get(stage)
    if model is None:
        model = stage_models[1]

    X = pd.DataFrame([row])[feature_cols]
    X_imp = imputer.transform(X)
    X_imp = pd.DataFrame(X_imp, columns=feature_cols)

    pred = float(model.predict(X_imp)[0])
    return max(0, min(100, pred))



# ---------------------------
# Save rolling last 10 predictions
# ---------------------------
def save_last_10(block):
    block = json_safe(block)
    if PRED_OUT.exists():
        try:
            old = json.loads(PRED_OUT.read_text())
            if not isinstance(old, list):
                old = []
        except:
            old = []
    else:
        old = []
    old.append(block)
    if len(old) > 10:
        old = old[-10:]
    PRED_OUT.write_text(json.dumps(old, indent=2))



# ---------------------------
# Continuous Prediction Loop
# ---------------------------
def main():
    print("[INFO] Loading models...")
    imputer, feature_cols, stage_models = load_models()

    print("[START] Continuous prediction loop...\n")
    last_ts = None

    while True:
        rows = read_latest_rows()
        if rows is None:
            time.sleep(3)
            continue

        ts = rows["timestamp"].iloc[0]
        if ts == last_ts:
            time.sleep(2)
            continue
        last_ts = ts

        manual = load_manual_stage()
        block = []

        for _, r in rows.iterrows():
            row = r.to_dict()

            # Stage from generator, unless manual override
            if row["node_id"] in manual:
                row["stage"] = manual[row["node_id"]]

            # Predict
            risk = predict_risk(row, stage_models, imputer, feature_cols)
            lvl = "LOW" if risk < 30 else "MEDIUM" if risk < 60 else "HIGH"

            obj = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "node_id": row["node_id"],
                "stage_used": int(row["stage"]),
                "risk_score": round(risk,3),
                "risk_level": lvl
            }

            print("[PRED]", obj)
            block.append(obj)

        save_last_10(block)
        write_hardware_output(block)
        time.sleep(3)



if __name__ == "__main__":
    main()
