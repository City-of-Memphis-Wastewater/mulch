# src/mulch/scaffold_loader.py

from pathlib import Path
from typing import Dict, Any, Optional, List
import toml
import json
import logging

from mulch.constants import FALLBACK_SCAFFOLD, DEFAULT_SCAFFOLD_FILENAME
from mulch.commands.dotfolder import create_dot_mulch
logger = logging.getLogger(__name__)

def load_scaffold_file(path: Path) -> Optional[Dict[str, Any]]:
    """Load scaffold configuration from file."""
    if not path.exists():
        return None
        
    try:
        return toml.load(path)
    except Exception as e:
        logger.warning(f"Failed to parse {path}: {e}")
        return None

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
    return FALLBACK_SCAFFOLD  # Now uses the TOML-based scaffold
