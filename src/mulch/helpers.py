from datetime import datetime
from pathlib import Path
import platform
import os
from typing import Union
import json
import toml
import typer
import logging
import sys
import subprocess

from mulch.constants import FALLBACK_SCAFFOLD


logger = logging.getLogger(__name__)


def calculate_nowtime_foldername():
    now = datetime.now()
    return now.strftime("%Y_%m%B_%d")

def resolve_first_existing_path(bases: list[Path], filenames: list[str]) -> Path | None:
    for base in bases:
        for name in filenames:
            candidate = base / name
            if candidate.exists():
                return candidate
    return None
    
def resolve_scaffold(order_of_respect: list[Path], filenames_of_respect: list[str]) -> dict:
    for base_path in order_of_respect:
        logger.info(f"base_path = {base_path}")
        logger.info(f"type(base_path) = {type(base_path)}")
        if not isinstance(base_path, Path):
            continue

        for filename in filenames_of_respect:
            candidate = Path(base_path) / filename
            if candidate.exists():
                try:
                    if candidate.suffix == ".toml":
                        typer.secho(f"📄 Loading scaffold from: {candidate}", fg=typer.colors.CYAN)
                        return toml.load(candidate)
                    elif candidate.suffix == ".json":
                        typer.secho(f"📄 Loading scaffold from: {candidate}", fg=typer.colors.CYAN)
                        with candidate.open("r", encoding="utf-8") as f:
                            return json.load(f)
                except Exception as e:
                    typer.secho(f"⚠️ Error loading scaffold from {candidate}: {e}", fg=typer.colors.RED)
                    logger.warning(f"Failed to load scaffold: {candidate}, error: {e}")
                    continue

    typer.secho("📦 Falling back to embedded scaffold structure.", fg=typer.colors.YELLOW)
    return FALLBACK_SCAFFOLD


def get_global_config_path(appname=None) -> Path:
    if platform.system() == "Windows":
        return Path(os.getenv("APPDATA", Path.home())) / appname
    else:
        return Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config")) / appname
    
def get_user_root(appname=None) -> Path:
    """
    Return the user's home config path for mulch, e.g.:
    - Windows: %USERPROFILE%
    - Linux/macOS: ~/.config
    """
    if platform.system() == "Windows":
        return Path(os.environ.get("USERPROFILE", Path.home())) / appname
    else:
        # Unix-like systems
        return Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / appname
    

def get_username_from_home_directory():
    home_dir = Path.home()  # Get the home directory
    return home_dir.name    # Extract the username from the home directory path

#VALID_EXTENSIONS = [".toml", ".json"]

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
def open_editor(file_path: Path):
    """Open the file in an appropriate system editor."""
    if sys.platform.startswith("win"):
        os.startfile(str(file_path))
    elif sys.platform == "darwin":
        subprocess.run(["open", str(file_path)])
    else:
        # For Linux: prefer $EDITOR, fallback to nano
        editor = os.getenv("EDITOR", "nano")
        subprocess.run([editor, str(file_path)])