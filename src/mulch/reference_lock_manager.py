import json
from pathlib import Path
from datetime import datetime

REFERENCE_LOCK_PATH = Path(".mulch/reference.lock")

def load_reference_lock() -> dict:
    if REFERENCE_LOCK_PATH.exists():
        with open(REFERENCE_LOCK_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "workspaces": {
            "paths": []
        },
        "src": {"path": None, "flags": []},
        "validation": {"is_consistent": True, "issues": []},
        "metadata": {"workspace_updated": None, "src_updated": None, "version": "0.1"},
    }

def build_flags(here: bool = False, stealth: bool = False) -> list[str]:
    flags = []
    if here:
        flags.append("--here")
    if stealth:
        flags.append("--stealth")
    return flags


REFERENCE_LOCK_PATH = Path(".mulch/reference.lock")

    
def save_reference_lock(data: dict):
    REFERENCE_LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REFERENCE_LOCK_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def validate_reference_lock(data: dict) -> dict:
    issues = []
    ws_paths = data.get("workspaces", {}).get("paths", [])
    src_path = data.get("src", {}).get("path")

    if not ws_paths:
        issues.append("No workspaces registered in reference.lock.")
    if not src_path:
        issues.append("Src path is not set in reference.lock.")

    # Additional validations can be added here, e.g. overlapping paths, flags inconsistencies, etc.

    data["validation"]["is_consistent"] = len(issues) == 0
    data["validation"]["issues"] = issues
    return data

class ReferenceLockManager:

    @staticmethod
    def load_lock() -> dict:
        return load_reference_lock()

    @staticmethod
    def save_lock(data: dict):
        save_reference_lock(data)

    @staticmethod
    def update_lock_workspace(path: Path, flags: list[str]) -> dict:
        path = str(path)
        data = load_reference_lock()
        now_iso = datetime.utcnow().isoformat() + "Z"

        workspaces = data.setdefault("workspaces", {})
        paths = workspaces.setdefault("paths", [])

        # Update existing or append new workspace entry by path
        for ws in paths:
            if ws["path"] == path:
                ws["flags"] = flags
                break
        else:
            paths.append({"path": path, "flags": flags})

        data.setdefault("metadata", {})
        data["metadata"]["workspace_updated"] = now_iso

        data = validate_reference_lock(data)
        save_reference_lock(data)
        return data

    @staticmethod
    def update_lock_src(path: Path, flags: list[str]) -> dict:
        path = str(path)
        data = load_reference_lock()
        now_iso = datetime.utcnow().isoformat() + "Z"

        data.setdefault("src", {})
        data["src"]["path"] = path
        data["src"]["flags"] = flags

        data.setdefault("metadata", {})
        data["metadata"]["src_updated"] = now_iso

        data = validate_reference_lock(data)
        save_reference_lock(data)
        return data
