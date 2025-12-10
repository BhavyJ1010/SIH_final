# src/api/app.py
"""
FastAPI backend for SIH_final Cloudburst EWS
- Hardware ingestion (/ingest/hardware)
- Prediction ingestion (/ingest/prediction)
- Manual stage control (/api/manual_stage)
- SSE stream of events (/stream/updates)
- GET endpoints for dashboard polling
- SMS alerts: Twilio if configured, else Textbelt fallback
"""

import os
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from sse_starlette.sse import EventSourceResponse
import requests

# Optional Twilio
try:
    from twilio.rest import Client as TwilioClient
except Exception:
    TwilioClient = None

# --- Paths / base ---
BASE = Path(__file__).resolve().parents[2]
DATA_DIR = BASE / "data"
MODELS_DIR = BASE / "models"
DATA_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)

HW_CSV = DATA_DIR / "hardware_node0.csv"      # append raw CSV logs (optional)
HW_JSON = DATA_DIR / "hardware_output.json"   # snapshot per node
PRED_JSON = DATA_DIR / "prediction.json"      # rolling blocks of predictions
STAGE_STATE = DATA_DIR / "stage_state.json"   # persistent stage per node
MANUAL_STAGE = DATA_DIR / "manual_stage.json" # manual override map
LIVE_CSV = DATA_DIR / "live.csv"              # optional live.csv

# In-memory queue for SSE
sse_queue: asyncio.Queue = asyncio.Queue()

app = FastAPI(title="SIH Cloudburst Backend (FastAPI + SSE)")

# Allow dashboard origin(s) — change for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Utility helpers --------------------------------------------------------

def safe_read_json(p: Path, default):
    try:
        if not p.exists():
            return default
        return json.loads(p.read_text())
    except Exception:
        return default

def safe_write_json(p: Path, obj):
    p.write_text(json.dumps(obj, indent=2))
    return True

def append_hw_csv(row: Dict[str, Any]):
    header = ["timestamp","node_id","temperature","pressure","humidity","rainfall_mm","wind_speed"]
    try:
        write_header = not HW_CSV.exists()
        with open(HW_CSV, "a", newline="") as f:
            if write_header:
                f.write(",".join(header) + "\n")
            vals = [str(row.get(k, "")) for k in header]
            f.write(",".join(vals) + "\n")
    except Exception:
        # silently ignore CSV writing errors
        pass

def json_safe(obj):
    """Convert numpy types to python native for JSON"""
    if isinstance(obj, (int, float, str, bool)) or obj is None:
        return obj
    if isinstance(obj, dict):
        return {k: json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [json_safe(v) for v in obj]
    try:
        return float(obj)
    except Exception:
        return str(obj)

# SMS helpers ------------------------------------------------------------

ALERT_NUMBERS = os.getenv("ALERT_NUMBERS", "")  # comma-separated
ALERT_LIST = [n.strip() for n in ALERT_NUMBERS.split(",") if n.strip()]

TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM = os.getenv("TWILIO_FROM")

TEXTBELT_API = "https://textbelt.com/text"

def send_sms_textbelt(message: str, numbers: List[str]) -> bool:
    """
    Simple Textbelt fallback. Free trial has limits.
    """
    sent_any = False
    for num in numbers:
        payload = {"phone": num, "message": message, "key": os.getenv("TEXTBELT_KEY", "textbelt")}
        try:
            r = requests.post(TEXTBELT_API, data=payload, timeout=6)
            j = r.json()
            if j.get("success"):
                sent_any = True
        except Exception:
            continue
    return sent_any

def send_sms_twilio(message: str, numbers: List[str]) -> bool:
    if not (TWILIO_SID and TWILIO_TOKEN and TWILIO_FROM and TwilioClient):
        return False
    try:
        client = TwilioClient(TWILIO_SID, TWILIO_TOKEN)
        for num in numbers:
            client.messages.create(body=message, from_=TWILIO_FROM, to=num)
        return True
    except Exception:
        return False

def send_alert_sms(message: str) -> bool:
    """
    Primary: Twilio (if configured)
    Fallback: Textbelt
    """
    numbers = ALERT_LIST
    if not numbers:
        return False
    ok = False
    if TWILIO_SID and TWILIO_TOKEN and TWILIO_FROM and TwilioClient:
        ok = send_sms_twilio(message, numbers)
    if not ok:
        ok = send_sms_textbelt(message, numbers)
    return ok

# SSE producer helper ---------------------------------------------------

async def publish_event(event: Dict[str, Any]):
    """Put a JSON-serializable event into the sse_queue"""
    try:
        await sse_queue.put(event)
    except Exception:
        pass

async def sse_event_stream():
    """
    Async generator that yields server-sent events whenever something is put into queue.
    Yields keep-alive comment every 15s to avoid proxies closing the connection.
    """
    while True:
        try:
            event = await asyncio.wait_for(sse_queue.get(), timeout=15.0)
            yield {"event": "update", "data": json.dumps(event)}
        except asyncio.TimeoutError:
            # keepalive
            yield {"event": "keepalive", "data": json.dumps({"ts": datetime.utcnow().isoformat()})}
        except Exception:
            await asyncio.sleep(1)

# Persistence helpers ----------------------------------------------------

def persist_prediction_block(block: List[Dict[str, Any]]):
    old = safe_read_json(PRED_JSON, [])
    old.append(block)
    # keep last 50 blocks
    if len(old) > 50:
        old = old[-50:]
    safe_write_json(PRED_JSON, old)

def persist_hardware_snapshot(node_id: str, payload: Dict[str, Any]):
    obj = safe_read_json(HW_JSON, {})
    obj[node_id] = payload
    safe_write_json(HW_JSON, obj)

def load_stage_state():
    return safe_read_json(STAGE_STATE, {})

def save_stage_state(state: Dict[str, Any]):
    safe_write_json(STAGE_STATE, state)

def load_manual_override():
    return safe_read_json(MANUAL_STAGE, {})

# --- End helpers --------------------------------------------------------

# API endpoints ----------------------------------------------------------

@app.get("/status")
def status():
    return {"ok": True, "time": datetime.utcnow().isoformat()}

@app.post("/ingest/hardware")
async def ingest_hardware(payload: dict):
    """
    Receive hardware sensor JSON from Raspberry Pi.
    Example payload:
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
    if not payload or "node_id" not in payload:
        raise HTTPException(400, "node_id required")
    node = payload["node_id"]
    # Append CSV for raw logging (best-effort)
    try:
        append_hw_csv(payload)
    except Exception:
        pass

    # Prepare snapshot
    snap = {
        "stage": payload.get("stage", 1),
        "temperature": payload.get("temperature"),
        "pressure": payload.get("pressure"),
        "humidity": payload.get("humidity"),
        "rainfall_mm": payload.get("rainfall_mm"),
        "wind_speed": payload.get("wind_speed"),
        "alert": payload.get("alert", "NORMAL"),
        "updated_at": datetime.utcnow().isoformat()
    }
    persist_hardware_snapshot(node, snap)

    # Publish SSE event
    await publish_event({"type": "hardware", "node": node, "payload": snap})

    return {"ok": True, "node": node}

@app.post("/ingest/prediction")
async def ingest_prediction(payload: dict):
    """
    Accepts a list (block) or a single prediction object.
    Each prediction object:
    {
      "timestamp": "2025-12-10 04:25:19",
      "node_id": "node0",
      "stage_used": 1,
      "risk_score": 52.472,
      "risk_level": "MEDIUM"
    }
    """
    if not payload:
        raise HTTPException(400, "payload required")
    block = None
    if isinstance(payload, list):
        block = payload
    elif isinstance(payload, dict):
        # allow single prediction or block wrapped in dict
        if all(k in payload for k in ("node_id","risk_score")):
            block = [payload]
        else:
            # fallback: wrap
            block = [payload]
    else:
        raise HTTPException(400, "invalid payload type")

    # persist
    persist_prediction_block(block)

    # Publish SSE event + optional SMS if high risk
    await publish_event({"type": "prediction_block", "block": block})

    # Check for high risk and send SMS if needed
    try:
        for p in block:
            score = float(p.get("risk_score", 0.0))
            if score >= 75.0:
                msg = f"ALERT: {p.get('node_id')} high risk={score:.1f} stage={p.get('stage_used')}"
                send_alert_sms(msg)
    except Exception:
        pass

    return {"ok": True, "len": len(block)}

@app.get("/api/hardware_output")
def api_hardware_output():
    return safe_read_json(HW_JSON, {})

@app.get("/api/predictions")
def api_predictions():
    return safe_read_json(PRED_JSON, [])

@app.get("/api/stage_state")
def api_stage_state():
    return load_stage_state()

@app.get("/api/live_latest")
def api_live_latest():
    """
    Return rows from live.csv that have the latest timestamp.
    If live.csv not present, return empty list.
    """
    if not LIVE_CSV.exists():
        return []
    import pandas as pd
    try:
        df = pd.read_csv(LIVE_CSV)
        if "timestamp" in df.columns:
            last = df["timestamp"].iloc[-1]
            df2 = df[df["timestamp"] == last]
            return df2.to_dict(orient="records")
        return df.tail(5).to_dict(orient="records")
    except Exception:
        return []

@app.post("/api/manual_stage")
def api_manual_stage(payload: dict):
    """
    Set manual stage override mapping, e.g. {"node0":2}
    """
    if not isinstance(payload, dict):
        raise HTTPException(400, "dict payload expected")
    safe_write_json(MANUAL_STAGE, payload)
    # publish event so UI can pick up
    asyncio.create_task(publish_event({"type": "manual_stage", "payload": payload}))
    return {"ok": True, "manual": payload}

@app.get("/stream/updates")
async def stream_updates(request: Request):
    """
    SSE stream of events. Client should connect and receive JSON events.
    """
    async def event_generator():
        async for ev in sse_event_stream():
            # If client closed connection, break
            if await request.is_disconnected():
                break
            # SSE Starlette expects dict with keys 'event' and 'data'
            yield ev
    return EventSourceResponse(event_generator())

# Minimal admin: set stage_state (for generator persistence)
@app.post("/api/stage_state")
def set_stage_state(payload: dict):
    if not isinstance(payload, dict):
        raise HTTPException(400, "dict payload expected")
    save_stage_state(payload)
    asyncio.create_task(publish_event({"type": "stage_state", "payload": payload}))
    return {"ok": True}

# Health and debug endpoints
@app.get("/api/debug")
def api_debug():
    return {
        "hw_snapshot": safe_read_json(HW_JSON, {}),
        "predictions": safe_read_json(PRED_JSON, [])[-3:],
        "stage_state": load_stage_state(),
        "manual_stage": load_manual_override()
    }

# Root
@app.get("/")
def root():
    return {"service": "SIH Cloudburst Backend", "time": datetime.utcnow().isoformat()}

# Run with: uvicorn app:app --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)
