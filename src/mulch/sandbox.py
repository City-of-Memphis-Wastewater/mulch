def evaluate_workspace_status(self) -> bool:
    if self.workspace_dir.exists():
        if self.space_lock_path.exists():
            try:
                with open(self.space_lock_path, "r", encoding="utf-8") as f:
                    existing = json.load(f)
                if existing.get("scaffold", {}) == self.lock_data["scaffold"]:
                    typer.secho("✅ Scaffold matches existing workspace. Nothing regenerated.", fg=typer.colors.BLUE)
                    return False
                else:
                    typer.confirm(
                        "⚠️ Workspace exists, but scaffold has changed.\nOverwrite workspace?",
                        abort=True
                    )
            except Exception as e:
                typer.confirm(
                    f"⚠️ Workspace exists but space.lock could not be read ({e}).\nOverwrite workspace?",
                    abort=True
                )
        else:
            typer.confirm(
                "⚠️ Workspace exists but no space.lock was found.\nOverwrite workspace?",
                abort=True
            )
    return True

def evaluate_manager_status(self) -> bool:
    if self.bare or self.here:
        return True  # Skip entirely

    if self.manager_lock_path.exists():
        try:
            with open(self.manager_lock_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
            existing_scaffold = existing.get("scaffold", {})
            if existing_scaffold != self.lock_data["scaffold"]:
                typer.confirm(
                    "⚠️ Your current scaffold differs from the one used to generate workspace_manager.py.\n"
                    f"Existing: {self.manager_lock_path}\nContinue?", abort=True
                )
        except Exception as e:
            logger.warning(f"Could not read manager.lock for comparison: {e}")


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


def load_scaffold(target_dir: Path | None = None) -> dict:
    target_dir = target_dir or Path.cwd()

    base_dirs = [
        target_dir / ".mulch",                              # 1. Local .mulch folder
        target_dir,                                         # 2. Project root
        Path.home() / "mulch",                              # 3. User root convention (if desired)
        get_global_config_path(appname="mulch")             # 4. Global config dir (e.g., ~/.config/mulch)
    ]

    filenames = ["mulch-scaffold.toml", "mulch-scaffold.json"]

    for base in base_dirs:
        for filename in filenames:
            path = base / filename
            scaffold = try_load_scaffold_file(path)
            if scaffold:
                logger.info(f"✅ Loaded scaffold from: {path}")
                return scaffold

    logger.warning("⚠️ No valid scaffold file found. Falling back to internal scaffold.")
    return FALLBACK_SCAFFOLD
