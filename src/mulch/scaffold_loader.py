# src/mulch/scaffold_loader.py

from pathlib import Path
from typing import Dict, Any, Optional, List
import toml
import json
import logging

from src.mulch.constants import FALLBACK_SCAFFOLD, DEFAULT_SCAFFOLD_FILENAME
from src.mulch.commands.dotfolder import create_dot_mulch
logger = logging.getLogger(__name__)

def load_scaffold_file(path: Path) -> Optional[Dict[str, Any]]:
    """
    Low-level function to read and parse a scaffold file.
    Supports both TOML and JSON formats.
    """
    if not path.exists():
        return None
        
    try:
        if path.suffix == '.toml':
            return toml.load(path)
        elif path.suffix == '.json':
            return json.loads(path.read_text())
    except Exception as e:
        logger.warning(f"Failed to parse {path}: {e}")
        return None

def load_scaffold(
    target_dir: Path,
    strict_local: bool = False,
    seed_if_missing: bool = False
) -> Dict[str, Any]:
    """
    Mid-level function to find and load scaffold from known locations.
    Falls back to defaults if needed.
    """
    base = target_dir / ".mulch"
    
    # In strict mode, only look in .mulch
    if strict_local:
        if not base.exists() and seed_if_missing:
            create_dot_mulch(target_dir)
        elif not base.exists():
            raise FileNotFoundError(f"No .mulch directory found in {target_dir}")
    
    return resolve_scaffold([base], ["mulch.toml"])

def resolve_scaffold(
    search_paths: List[Path],
    filenames: List[str]
) -> Dict[str, Any]:
    """
    High-level function to resolve scaffold across multiple possible locations.
    Follows order of precedence rules.
    """
    for base in search_paths:
        for filename in filenames:
            path = base / filename
            data = load_scaffold_file(path)
            if data:
                logger.info(f"📄 Loaded scaffold from: {path}")
                return data
    
    logger.warning("No valid scaffold file found, using fallback")
    return FALLBACK_SCAFFOLD