# src/mulch/active_workspace_manager.py

import toml
from pathlib import Path
from datetime import datetime

ACTIVE_WORKSPACE_PATH = Path(".mulch/active_workspace.toml")

def load_active_workspace() -> dict:
    if ACTIVE_WORKSPACE_PATH.exists():
        return toml.load(ACTIVE_WORKSPACE_PATH)
    return {"path": None, "activated_at": None}

def save_active_workspace(path: str):
    ACTIVE_WORKSPACE_PATH.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "path": path,
        "activated_at": datetime.utcnow().isoformat() + "Z",
    }
    with open(ACTIVE_WORKSPACE_PATH, "w", encoding="utf-8") as f:
        toml.dump(data, f)

def clear_active_workspace():
    if ACTIVE_WORKSPACE_PATH.exists():
        ACTIVE_WORKSPACE_PATH.unlink()
