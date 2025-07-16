# src/mulch/scaffold_loader.py

import toml, json
from pathlib import Path

def load_scaffold_file(path: Path) -> dict | None:
    try:
        if path.suffix == ".json":
            return json.loads(path.read_text(encoding="utf-8"))
        elif path.suffix == ".toml":
            return toml.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Failed to load scaffold from {path}: {e}")
    return None