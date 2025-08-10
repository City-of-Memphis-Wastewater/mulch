
import toml
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

FALLBACK_SCAFFOLD = {...}  # your fallback dict
VALID_EXTENSIONS = [".toml", ".json"]

def try_load_scaffold_file(path: Path) -> dict | None:
    try:
        if not path.exists():
            return None

        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                logger.warning(f"{path} is empty. Continuing to next scaffold source.")
                return None

            if path.suffix == ".json":
                return json.loads(content)
            elif path.suffix == ".toml":
                return toml.loads(content)
            else:
                logger.warning(f"Unsupported scaffold file type: {path}")
    except Exception as e:
        logger.warning(f"Failed to load scaffold from {path}: {e}")
    return None

