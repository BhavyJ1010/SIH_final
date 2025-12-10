# realtime_predictor.py
import os
import json
from pathlib import Path
from datetime import datetime
import joblib
import pandas as pd
import numpy as np

BASE = Path(__file__).resolve().parents[2]   # SIH_final/
DATA_DIR = BASE / "data"
MODELS_DIR = BASE / "models"

LIVE_CSV = DATA_DIR / "live.csv"
MANUAL_STAGE_FILE = DATA_DIR / "manual_stage.json"
PRED_OUT = DATA_DIR / "prediction.json"
PREPROC_FILE = MODELS_DIR / "preprocessing.joblib"

# Model file names (optional - check existence)
STG1_MODEL = MODELS_DIR / "stage1_model.pkl"
STG2_MODEL = MODELS_DIR / "stage2_model.pkl"
STG3_MODEL = MODELS_DIR / "stage3_model.pkl"
CLASSIFIER_FILE = MODELS_DIR / "stage_classifier.pkl"

def load_models():
    preproc = None
    if PREPROC_FILE.exists():
        preproc = joblib.load(PREPROC_FILE)
        imputer = preproc.get("imputer")
        feature_cols = preproc.get("feature_cols")
    else:
        imputer = None
        feature_cols = None

    # load regressors if available
    stage_models = {}
    if STG1_MODEL.exists():
        stage_models[1] = joblib.load(STG1_MODEL)
    if STG2_MODEL.exists():
        stage_models[2] = joblib.load(STG2_MODEL)
    if STG3_MODEL.exists():
        stage_models[3] = joblib.load(STG3_MODEL)

    # classifier
    stage_classifier = None
    inv_class_map = None
    if CLASSIFIER_FILE.exists():
        obj = joblib.load(CLASSIFIER_FILE)
        stage_classifier = obj.get("model")
        class_map = obj.get("class_map")
        if class_map:
            inv_class_map = {v:k for k,v in class_map.items()}

    return imputer, feature_cols, stage_models, stage_classifier, inv_class_map

def read_latest_live_rows():
    if not LIVE_CSV.exists():
        print("[ERROR] live.csv not found at", LIVE_CSV)
        return None
    df = pd.read_csv(LIVE_CSV)
    if df.empty:
        print("[ERROR] live.csv empty")
        return None
    # last timestamp present
    last_ts = df["timestamp"].iloc[-1]
    # get all rows with that timestamp (all nodes)
    rows = df[df["timestamp"] == last_ts].copy()
    return rows

def load_manual_map():
    if not MANUAL_STAGE_FILE.exists():
        return {}
    try:
        d = json.loads(MANUAL_STAGE_FILE.read_text())
        if isinstance(d, dict):
            return {k:int(v) for k,v in d.items()}
    except Exception:
        pass
    return {}

def determine_stage_for_row(row, imputer, feature_cols, stage_classifier, inv_class_map, manual_map):
    node_id = row["node_id"]
    # manual override takes precedence
    if node_id in manual_map:
        return int(manual_map[node_id])

    # if classifier available and feature cols present
    if stage_classifier is not None and feature_cols is not None and imputer is not None:
        # build X using feature_cols, but ensure all exist
        X = pd.DataFrame([row])[feature_cols].fillna(0)
        X_imp = imputer.transform(X)
        pred = stage_classifier.predict(X_imp)[0]
        if inv_class_map:
            return int(inv_class_map.get(pred, 1))
        else:
            # if mapping not available assume pred+1
            return int(pred) + 1
    # fallback default
    return int(row.get("stage", 1))

def predict_for_row(row, imputer, feature_cols, stage_models):
    # prepare feature vector same as training
    if feature_cols is None or imputer is None:
        # fallback: simple heuristic risk from stage
        stage = int(row.get("stage", 1))
        return float(10 * stage)
    X = pd.DataFrame([row])[feature_cols].fillna(0)
    X_imp = imputer.transform(X)
    stage_used = int(row.get("stage", 1))
    model = stage_models.get(stage_used)
    if model is None:
        # fallback to lowest stage model available
        model = stage_models.get(1) or next(iter(stage_models.values()))
    pred = float(model.predict(X_imp)[0])
    pred = max(0.0, min(100.0, pred))
    return pred

def main():
    imputer, feature_cols, stage_models, stage_classifier, inv_class_map = load_models()
    rows = read_latest_live_rows()
    if rows is None:
        return
    manual_map = load_manual_map()

    results = []
    for _, r in rows.iterrows():
        row = r.to_dict()
        stage = determine_stage_for_row(row, imputer, feature_cols, stage_classifier, inv_class_map, manual_map)
        row["stage_used"] = stage
        # predict using appropriate model (or fallback)
        risk = predict_for_row(row, imputer, feature_cols, stage_models)
        level = "LOW" if risk < 30 else ("MEDIUM" if risk < 60 else "HIGH")
        out = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "node_id": row.get("node_id"),
            "stage_used": int(stage),
            "risk_score": float(round(risk,3)),
            "risk_level": level
        }
        results.append(out)
        print("[PRED]", out)

    # Save predictions array (list) to prediction.json
    try:
        PRED_OUT.write_text(json.dumps(results, indent=2))
        print("[INFO] Saved predictions to", PRED_OUT)
    except Exception as e:
        print("[ERROR] saving prediction:", e)

if __name__ == "__main__":
    main()

