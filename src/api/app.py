# ================================================================
# FastAPI Backend for SIH Cloudburst Early Warning System
# Clean, stable, Render-compatible, fully JSON-safe
# ================================================================

import os
import json
import asyncio
import requests
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
import pandas as pd

# ----------------------------------------------------------------
# PATHS
# ----------------------------------------------------------------
BASE = Path(__file__).resolve().parents[2]
DATA = BASE / "data"
DATA.mkdir(exist_ok=True)

LIVE_CSV = DATA / "live.csv"
PRED_JSON = DATA / "prediction.json"
HW_JSON = DATA / "hardware_output.json"
STAGE_STATE = DATA / "stage_state.json"
MANUAL_STAGE = DATA / "manual_stage.json"

# ----------------------------------------------------------------
# FASTAPI SETUP
# ----------------------------------------------------------------
app = FastAPI(title="SIH Cloudburst Backend", version="1.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------------------
# HELPERS
# ----------------------------------------------------------------

def safe_read(path, default):
    try:
        if path.exists():
            return json.loads(path.read_text())
    except:
        pass
    return default

def safe_write(path, obj):
    path.write_text(json.dumps(obj, indent=2))

# SSE Queue for live updates
sse_queue = asyncio.Queue()

async def publish(event):
    await sse_queue.put(event)

async def sse_stream():
    while True:
        try:
            event = await asyncio.wait_for(sse_queue.get(), timeout=12)
            yield {"event": "update", "data": json.dumps(event)}
        except asyncio.TimeoutError:
            # keep-alive
            yield {"event": "keepalive", "data": json.dumps({"ts": datetime.utcnow().isoformat()})}

# ----------------------------------------------------------------
# BASIC ENDPOINTS
# ----------------------------------------------------------------

@app.get("/")
def root():
    return {"backend": "running", "time": datetime.utcnow().isoformat()}


@app.get("/status")
def status():
    return {"ok": True}


# ----------------------------------------------------------------
# LIVE CSV READER
# ----------------------------------------------------------------
@app.get("/api/live_latest")
def api_live_latest():
    if not LIVE_CSV.exists():
        return []

    try:
        df = pd.read_csv(LIVE_CSV)
        if df.empty:
            return []
        last = df["timestamp"].iloc[-1]
        out = df[df["timestamp"] == last].to_dict(orient="records")
        return out
    except Exception as e:
        raise HTTPException(500, str(e))


# ----------------------------------------------------------------
# HARDWARE SNAPSHOT
# ----------------------------------------------------------------
@app.get("/api/hardware_output")
def api_hw():
    return safe_read(HW_JSON, {})


# ----------------------------------------------------------------
# PREDICTION HISTORY
# ----------------------------------------------------------------
@app.get("/api/predictions")
def api_predictions():
    return safe_read(PRED_JSON, [])


# ----------------------------------------------------------------
# MANUAL STAGE OVERRIDE
# ----------------------------------------------------------------
@app.post("/api/manual_stage")
def api_manual_stage(payload: dict):
    if not isinstance(payload, dict):
        raise HTTPException(400, "dict required")
    safe_write(MANUAL_STAGE, payload)
    asyncio.create_task(publish({"type": "manual_override", "payload": payload}))
    return {"ok": True, "manual": payload}


# ----------------------------------------------------------------
# HARDWARE INGEST (Raspberry Pi)
# ----------------------------------------------------------------
@app.post("/ingest/hardware")
async def ingest_hardware(payload: dict):
    if "node_id" not in payload:
        raise HTTPException(400, "node_id missing")

    node = payload["node_id"]

    snapshot = {
        "stage": payload.get("stage", 1),
        "temperature": payload.get("temperature"),
        "pressure": payload.get("pressure"),
        "humidity": payload.get("humidity"),
        "rainfall_mm": payload.get("rainfall_mm"),
        "wind_speed": payload.get("wind_speed"),
        "alert": payload.get("alert", "NORMAL"),
        "updated_at": datetime.utcnow().isoformat(),
    }

    current = safe_read(HW_JSON, {})
    current[node] = snapshot
    safe_write(HW_JSON, current)

    await publish({"type": "hw_update", "node": node, "data": snapshot})

    return {"ok": True}


# ----------------------------------------------------------------
# PREDICTOR INGEST
# ----------------------------------------------------------------
@app.post("/ingest/prediction")
async def ingest_prediction(payload):
    """
    payload = list of prediction objects (block)
    """
    if isinstance(payload, dict):
        payload = [payload]

    old = safe_read(PRED_JSON, [])
    old.append(payload)
    old = old[-20:]
    safe_write(PRED_JSON, old)

    await publish({"type": "prediction", "block": payload})

    return {"ok": True, "count": len(payload)}


# ----------------------------------------------------------------
# SSE STREAM
# ----------------------------------------------------------------
@app.get("/stream/updates")
async def stream_updates(request: Request):
    async def event_gen():
        async for ev in sse_stream():
            if await request.is_disconnected():
                break
            yield ev

    return EventSourceResponse(event_gen())
