# hardware_output_writer.py
# Writes a simple hardware_output.json file after every prediction cycle.

import json
import os
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
DATA_DIR = BASE / "data"
OUT_FILE = DATA_DIR / "hardware_output.json"


def write_hardware_output(pred_block):
    """
    pred_block = list of predictions (one per node)
    Example element:
    {
      "timestamp": "2025-12-10 10:32:00",
      "node_id": "node0",
      "stage_used": 2,
      "risk_score": 78.33,
      "risk_level": "HIGH"
    }
    """

    out = {}

    for p in pred_block:
        node = p["node_id"]
        stage = p["stage_used"]
        risk = p["risk_score"]
        lvl = p["risk_level"]

        alert = "NORMAL"
        if lvl == "MEDIUM":
            alert = "WARNING"
        elif lvl == "HIGH":
            alert = "HIGH_RISK"

        out[node] = {
            "stage": int(stage),
            "risk": float(risk),
            "alert": alert
        }

    OUT_FILE.write_text(json.dumps(out, indent=2))
    return out
