"""Run a trusted local manifest in this process so Task Scheduler owns the job."""

import contextlib
import hashlib
import json
import os
from pathlib import Path
import runpy
import sys
import traceback
from datetime import datetime, timezone


def run(manifest_path):
    payload = Path(manifest_path).read_bytes()
    spec = json.loads(payload.decode("utf-8-sig"))
    if not isinstance(spec.get("args"), list) or not all(isinstance(x, str) for x in spec["args"]):
        raise ValueError("args must be an array of strings")
    for field in ("script", "cwd", "log"):
        if not Path(spec[field]).is_absolute():
            raise ValueError(f"{field} must be absolute")
    script = Path(spec["script"]).resolve(strict=True)
    os.chdir(spec["cwd"])
    sys.argv = [str(script), *spec["args"]]
    sys.path.insert(0, str(script.parent))
    with Path(spec["log"]).open("a", encoding="utf-8", buffering=1) as log:
        with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
            print(json.dumps({
                "started": datetime.now(timezone.utc).isoformat(),
                "pid": os.getpid(),
                "manifest_sha256": hashlib.sha256(payload).hexdigest(),
                "script_sha256": hashlib.sha256(script.read_bytes()).hexdigest(),
            }), flush=True)
            try:
                runpy.run_path(str(script), run_name="__main__")
            except BaseException:
                traceback.print_exc()
                raise
            finally:
                log.flush()
                os.fsync(log.fileno())


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: run_job.py /absolute/path/to/private/manifest.json")
    run(sys.argv[1])
