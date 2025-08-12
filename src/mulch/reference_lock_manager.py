import json
from pathlib import Path
from datetime import datetime

REFERENCE_LOCK_PATH = Path(".mulch/reference.lock")

def load_reference_lock() -> dict:
    if REFERENCE_LOCK_PATH.exists():
        with open(REFERENCE_LOCK_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "workspaces": {"instances": []},
        "src": {"instances": []},
        "validation": {"is_consistent": True, "issues": []},
        "metadata": {"workspace_updated": None, "src_updated": None, "version": "0.1"},
    }

def build_flags_record(here: bool = False, stealth: bool = False, force: bool = False, 
                       name: str = None, pattern: str = None,expliref: str = None) -> list[str]:
    flags = []
    if here:
        flags.append("--here")
    if stealth:
        flags.append("--stealth")
    if force:
        flags.append("--force")
    if name:
        flags.append("--name")
        print("\nNAME FLAG ADDED\n")
    if pattern:
        flags.append("--pattern")
    if expliref:
        flags.append("--expliref")
    return flags


REFERENCE_LOCK_PATH = Path(".mulch/reference.lock")

    
def save_reference_lock(data: dict):
    REFERENCE_LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REFERENCE_LOCK_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def validate_reference_lock(data: dict) -> dict:
    issues = []
    ws_paths = data.get("workspaces", {}).get("instances", [])
    src_paths = data.get("src", {}).get("instances", [])

    if not ws_paths:
        issues.append("No workspaces registered in reference.lock.")
    if not src_paths:
        issues.append("No src instances registered in reference.lock.")

    # Additional validation...

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
    def update_lock_workspace(pathstr: str, flags: list[str]) -> dict:
        """ Update or add a workspace entry in the reference lock file. """

        # use pathstr instead of path to avoid Path serialization issues, and to allow "null" as a string
        path = str(pathstr) # in case a Path object is passed, but can also be "null"
        data = load_reference_lock()
        now_iso = datetime.utcnow().isoformat() + "Z"

        workspaces = data.setdefault("workspaces", {})
        instances = workspaces.setdefault("instances", [])

        # Update existing or append new workspace entry by path
        for ws in instances:
            if ws["path"] == path:
                ws["flags"] = flags
                break
        else:
            instances.append({"path": path, "flags": flags})

        data.setdefault("metadata", {})
        data["metadata"]["workspace_updated"] = now_iso

        data = validate_reference_lock(data)
        save_reference_lock(data)
        return data

    @staticmethod
    def update_lock_src(pathstr: str, flags: list[str]) -> dict:
        path = str(pathstr)
        data = load_reference_lock()
        now_iso = datetime.utcnow().isoformat() + "Z"

        src = data.setdefault("src", {})
        instances = src.setdefault("instances", [])

        # Update existing or append new src entry by path
        for sourcepath in instances:
            if sourcepath["path"] == path:
                sourcepath["flags"] = flags
                break
        else:
            instances.append({"path": path, "flags": flags})

        data.setdefault("metadata", {})
        data["metadata"]["src_updated"] = now_iso

        data = validate_reference_lock(data)
        save_reference_lock(data)
        return data
    
    @staticmethod
    def list_workspaces() -> list[dict]:
        data = load_reference_lock()
        return data.get("workspaces", {}).get("instances", [])

    @staticmethod
    def list_src() -> list[dict]:
        data = load_reference_lock()
        return data.get("src", {}).get("instances", [])