"""SYNTHETIC infrastructure demo. Restart saves completed steps without duplication."""

import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path


def now():
    return datetime.now(timezone.utc).isoformat()


def validate(state, total):
    if state.get("synthetic_only") is not True or state.get("total") != total:
        raise ValueError("Not this synthetic checkpoint or target changed")
    steps = state["steps"]
    if len(steps) > total or [x["step"] for x in steps] != list(range(1, len(steps) + 1)):
        raise ValueError("Non-contiguous or duplicate checkpoint steps")
    if any(x["value"] != x["step"] ** 2 for x in steps):
        raise ValueError("Corrupt synthetic values")


def save(path, state):
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(state, handle, indent=2)
        handle.flush()
        os.fsync(handle.fileno())
    # Windows readers/scanners can briefly deny replacement. Keep the old
    # checkpoint intact and retry only known Windows sharing/access errors.
    for attempt in range(20):
        try:
            os.replace(temporary, path)
            return
        except PermissionError as error:
            if getattr(error, "winerror", None) not in (5, 32, 33) or attempt == 19:
                raise
            time.sleep(0.05)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--steps", type=int, default=300)
    parser.add_argument("--delay", type=float, default=2.0)
    args = parser.parse_args()
    if args.steps < 1 or args.delay < 0:
        parser.error("steps must be positive and delay non-negative")
    args.state.parent.mkdir(parents=True, exist_ok=True)
    if args.state.exists():
        state = json.loads(args.state.read_text(encoding="utf-8"))
    else:
        state = {"synthetic_only": True, "total": args.steps, "steps": [], "sessions": []}
    validate(state, args.steps)
    state["sessions"].append({"pid": os.getpid(), "started": now(), "resume_after": len(state["steps"])})
    state["status"] = "running"
    save(args.state, state)
    for step in range(len(state["steps"]) + 1, args.steps + 1):
        time.sleep(args.delay)
        state["steps"].append({"step": step, "value": step ** 2})
        state["updated"] = now()
        save(args.state, state)
        print(f"SYNTHETIC completed step {step}", flush=True)
    state["status"] = "completed"
    save(args.state, state)


if __name__ == "__main__":
    main()
