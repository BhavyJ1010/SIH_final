# app.py  (FastAPI backend)
# Place at SIH_final/src/api/app.py

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import json
import uvicorn
from datetime import datetime

BASE = Path(__file__).resolve().parents[2]
DATA_DIR = BASE / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

HW_IN = DATA_DIR / "hardware_node0.csv"        # optional CSV for hardware raw logging
HW_JSON = DATA_DIR / "hardware_output.json"    # final hardware output used by devices
PRED_JSON = DATA_DIR / "prediction.json"
STAGE_STATE = DATA_DIR / "stage_state.json"
MANUAL_STAGE = DATA_DIR / "manual_stage.json"
LIVE_CSV = DATA_DIR / "live.csv"

app = FastAPI(title="Cloudburst EWS Backend")

# allow dashboard + devices (set origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET","POST","OPTIONS"],
    allow_headers=["*"],
)

def safe_write(path: Path, obj):
    path.write_text(json.dumps(obj, indent=2))

@app.get("/status")
def status():
    return {"status":"ok", "time": datetime.now().isoformat()}

# Hardware ingestion endpoint: devices (Raspberry Pi / Arduino gateway) POST sensor JSON
@app.post("/ingest/hardware")
async def ingest_hardware(payload: dict):
    """
    Expects JSON like:
    {
      "timestamp": "2025-12-10T07:30:00",
      "node_id": "node0",
      "temperature": 27.4,
      "pressure": 1008.2,
      "humidity": 70.1,
      "rainfall_mm": 0.0,
      "wind_speed": 5.4
    }
    """
    if not payload.get("node_id"):
        raise HTTPException(status_code=400, detail="node_id required")
    # optional: append to CSV for raw logging
    try:
        # append to csv (simple append, create if missing)
        import csv
        header = ["timestamp","node_id","temperature","pressure","humidity","rainfall_mm","wind_speed"]
        row = [payload.get(h,"") for h in header]
        write_header = not HW_IN.exists()
        with open(HW_IN, "a", newline="") as f:
            writer = csv.writer(f)
            if write_header:
                writer.writerow(header)
            writer.writerow(row)
    except Exception as e:
        # non-fatal
        pass
    # update hardware_output.json minimal (consumer friendly)
    # We'll not modify stage here. This file shows latest hardware values for node0.
    hw_out = {}
    if HW_JSON.exists():
        try:
            hw_out = json.loads(HW_JSON.read_text())
        except:
            hw_out = {}
    # write hardware live snapshot under node_id
    node = payload["node_id"]
    hw_out[node] = {
        "stage": payload.get("stage", 1),
        "temperature": payload.get("temperature"),
        "pressure": payload.get("pressure"),
        "humidity": payload.get("humidity"),
        "rainfall_mm": payload.get("rainfall_mm"),
        "wind_speed": payload.get("wind_speed"),
        "alert": payload.get("alert","NORMAL"),
        "updated_at": datetime.now().isoformat()
    }
    safe_write(HW_JSON, hw_out)
    return {"ok": True}

# Predictor / UI can POST predictions here (or backend can update)
@app.post("/ingest/prediction")
async def ingest_prediction(payload: dict):
    """
    Accepts a block/list or single prediction.
    Example: [{"timestamp": "...","node_id":"node0","stage_used":1,"risk_score":12.3,"risk_level":"LOW"}, ...]
    """
    try:
        old = []
        if PRED_JSON.exists():
            old = json.loads(PRED_JSON.read_text())
        # ensure list of blocks. We'll append the incoming block as latest
        if isinstance(payload, list):
            block = payload
        elif isinstance(payload, dict):
            # single prediction or a block - normalize
            if all(k in payload for k in ("node_id","risk_score")):
                block = [payload]
            else:
                block = [payload]
        else:
            raise
        old.append(block)
        # keep last 20 blocks to be safe
        if len(old) > 20:
            old = old[-20:]
        safe_write(PRED_JSON, old)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"ok": True}

# Simple GET endpoints to allow dashboard to request latest state
@app.get("/api/hardware_output")
def get_hardware_output():
    if not HW_JSON.exists():
        return {}
    try:
        return json.loads(HW_JSON.read_text())
    except:
        return {}

@app.get("/api/predictions")
def get_predictions():
    if not PRED_JSON.exists():
        return []
    try:
        return json.loads(PRED_JSON.read_text())
    except:
        return []

@app.get("/api/stage_state")
def get_stage_state():
    if not STAGE_STATE.exists():
        return {}
    try:
        return json.loads(STAGE_STATE.read_text())
    except:
        return {}

@app.get("/api/live_latest")
def get_live_latest():
    # return last timestamp rows of live.csv as list of dicts
    if not LIVE_CSV.exists():
        return []
    import pandas as pd
    try:
        df = pd.read_csv(LIVE_CSV)
        if "timestamp" in df.columns:
            last = df["timestamp"].iloc[-1]
            df2 = df[df["timestamp"] == last].to_dict(orient="records")
            return df2
        return df.tail(5).to_dict(orient="records")
    except Exception:
        return []

# Endpoint to set manual stage (from dashboard)
@app.post("/api/manual_stage")
def set_manual_stage(payload: dict):
    # payload example: {"node0":2}
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="dict expected")
    safe_write(MANUAL_STAGE, payload)
    # Optionally, reflect in stage_state file so generator reads it quickly
    # We will not override stage_state here, generator handles reading manual file
    return {"ok": True, "manual_stage": payload}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

