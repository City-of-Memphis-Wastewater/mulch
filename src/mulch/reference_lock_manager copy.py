# src/mulch/reference_lock_manager.py

import toml
from pathlib import Path
from datetime import datetime

REFERENCE_LOCK_PATH = Path(".mulch/reference.lock")

def load_reference_lock() -> dict:
    if REFERENCE_LOCK_PATH.exists():
        return toml.load(REFERENCE_LOCK_PATH)
    return {
        "workspace": {"path": None, "flags": []},
        "src": {"path": None, "flags": []},
        "validation": {"is_consistent": True, "issues": []},
        "metadata": {"workspace_updated": None, "src_updated": None, "version": "0.1"},
    }

def save_reference_lock(data: dict):
    REFERENCE_LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REFERENCE_LOCK_PATH, "w", encoding="utf-8") as f:
        toml.dump(data, f)

def validate_reference_lock(data: dict) -> dict:
    issues = []
    ws_list = data.get("workspaces", [])
    src_flags = data.get("src", {}).get("flags", [])
    src_path = data.get("src", {}).get("path")

    # Basic example validations:
    if not ws_list:
        issues.append("No workspaces registered in reference.lock.")
    if not src_path:
        issues.append("Src path is not set in reference.lock.")

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
    def update_lock(part: str, path: str, flags: list[str]) -> dict:
        data = load_reference_lock()
        now_iso = datetime.utcnow().isoformat() + "Z"

        data.setdefault(part, {})
        data[part]["path"] = path
        data[part]["flags"] = flags

        if part == "workspace":
            data.setdefault("metadata", {})
            data["metadata"]["workspace_updated"] = now_iso
        elif part == "src":
            data.setdefault("metadata", {})
            data["metadata"]["src_updated"] = now_iso

        data = validate_reference_lock(data)
        save_reference_lock(data)
        return data

    @staticmethod
    def update_lock_from_src(stealth: bool, src_path: Path):
        flags = ["--stealth"] if stealth else []
        return ReferenceLockManager.update_lock(
            part="src",
            path=str(src_path),
            flags=flags
        )

    @staticmethod    
    def update_reference_lock_src(path: str, flags: list[str]) -> dict:
        data = load_reference_lock()
        now_iso = datetime.utcnow().isoformat() + "Z"

        data.setdefault("src", {})
        data["src"]["path"] = path
        data["src"]["flags"] = flags

        data.setdefault("metadata", {})
        data["metadata"]["last_updated"] = now_iso

        data = validate_reference_lock(data)
        save_reference_lock(data)
        return data



    @staticmethod
    def update_lock_from_workspace(here: bool, workspace_path: Path):
        flags = ["--here"] if here else []
        return ReferenceLockManager.update_lock(
            part="workspace",
            path=str(workspace_path),
            flags=flags
        )
    
    @staticmethod
    def update_reference_lock_workspace(path: str, flags: list[str]) -> dict:
        data = load_reference_lock()
        now_iso = datetime.utcnow().isoformat() + "Z"

        ws_list = data.setdefault("workspaces", [])
        # Update or add workspace entry by path
        for ws in ws_list:
            if ws["path"] == path:
                ws["flags"] = flags
                break
        else:
            ws_list.append({"path": path, "flags": flags})

        data.setdefault("metadata", {})
        data["metadata"]["last_updated"] = now_iso

        data = validate_reference_lock(data)
        save_reference_lock(data)
        return data