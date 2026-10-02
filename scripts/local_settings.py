"""Configuration for this checkout only; never reads operational audit files."""

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / ".local"


def load_settings():
    spec = json.loads((LOCAL / "settings.json").read_text(encoding="utf-8-sig"))
    if type(spec.get("port")) is not int or not 1024 <= spec["port"] <= 65535:
        raise ValueError("Expected an unprivileged integer port")
    for field in ("project", "python"):
        path = Path(spec[field])
        if not path.is_absolute() or not path.exists():
            raise ValueError(f"Missing absolute {field} path")
    if not Path(spec["project"]).is_dir() or not Path(spec["python"]).is_file():
        raise ValueError("Expected project directory and Python executable")
    return spec


def configure_jupyter_environment():
    for variable, folder in (
        ("JUPYTER_CONFIG_DIR", "config"),
        ("JUPYTER_DATA_DIR", "data"),
        ("JUPYTER_RUNTIME_DIR", "runtime"),
    ):
        path = LOCAL / folder
        if not path.is_dir():
            raise RuntimeError("Run Initialize-Local.ps1 first")
        os.environ[variable] = str(path)
