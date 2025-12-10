# set_manual_stage.py
import json
from pathlib import Path
import sys

BASE = Path(__file__).resolve().parents[2]
DATA_DIR = BASE / "data"
MANUAL_FILE = DATA_DIR / "manual_stage.json"

def set_manual(mapping):
    MANUAL_FILE.write_text(json.dumps(mapping, indent=2))
    print("Wrote manual_stage.json:", mapping)

def clear_manual():
    if MANUAL_FILE.exists():
        MANUAL_FILE.unlink()
        print("Cleared manual_stage.json")
    else:
        print("manual_stage.json not present")

if __name__ == "__main__":
    # Usage:
    # python set_manual_stage.py node0 2  -> sets {"node0": 2}
    # python set_manual_stage.py clear     -> clears file
    args = sys.argv[1:]
    if not args:
        print("Usage: python set_manual_stage.py <node_id> <stage>  OR  python set_manual_stage.py clear")
        sys.exit(1)
    if args[0].lower() == "clear":
        clear_manual()
    else:
        if len(args) < 2:
            print("Usage: python set_manual_stage.py <node_id> <stage>")
            sys.exit(1)
        node = args[0]
        try:
            st = int(args[1])
        except:
            print("Stage must be integer 1/2/3")
            sys.exit(1)
        set_manual({node: st})
