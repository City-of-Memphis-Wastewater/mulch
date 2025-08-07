# src/mulch/workspace_manager_generator.py (project-agnostic, reusable)

import json
import logging
from pathlib import Path
from jinja2 import Environment, PackageLoader, select_autoescape #,FileSystemLoader
import toml
import typer
from importlib.resources import files

from mulch.helpers import get_global_config_path, get_user_root, try_load_scaffold_file
from mulch.constants import FALLBACK_SCAFFOLD, DEFAULT_SCAFFOLD_FILENAME
from mulch.logging_setup import setup_logging, setup_logging_portable
from mulch.flags_log_status import FlagsLockStatus
from mulch.basepath_manager import PathContext


setup_logging_portable()
logger = logging.getLogger(__name__)


class WorkspaceManagerGenerator:
    f"""
    workspace manager generator for use with the mulch CLI command `mulch init`.
    Manages directory creation and standardized file placement based on {DEFAULT_SCAFFOLD_FILENAME}.
    """
    
    DEFAULT_WORKSPACE_CONFIG_FILENAME = "default-workspace.toml"
    DEFAULT_TEMPLATE_DIR = Path(__file__).parent / "templates"
    DEFAULT_WORKSPACE_TEMPLATE_FILENAME = "workspace_manager.py.j2"
    FALLBACK_SCAFFOLD = FALLBACK_SCAFFOLD # to make accessible, for pip and interally
    DEFAULT_SCAFFOLD_FILENAME = DEFAULT_SCAFFOLD_FILENAME # to make accessible, for pip and interally
    

    def __init__(self, base_path: Path, lock_data: dict, stealth: bool = False):
        """
        WorkspaceManagerGenerator.context is a mystery to me.
        """
        self.base_path = Path(base_path).resolve()
        self.lock_data = lock_data
        self.stealth = stealth 
        self.context = PathContext(base_path, workspace_name=None, here=None, stealth=stealth)
        self.flags_lock_path = self.context.flags_lock_path
        self.manager_lock_path = self.context.manager_lock_path
        self.manager_path = self.context.manager_path 
        self.project_name = self.base_path.name # assumption that the target dir is the package name, fair enough

    def get_path(self, key: str) -> Path:
        """
        Generic path getter using slash-separated key within the workspace.
        """
        path = self.workspace_dir
        for part in key.strip("/").split("/"):
            path /= part
        return path
    def evaluate_flags_lock_status(self) -> FlagsLockStatus:
        if not self.flags_lock_path.exists():
            return FlagsLockStatus.MISSING
        else:
            try:
                with open(self.flags_lock_path, "r", encoding="utf-8") as f:
                    existing = toml.loads(f)
            except:
                pass
        
    def build_src_components(self):
        setup_logging()
        was_source_generated = self.render_workspace_manager()
        return was_source_generated

    def render_workspace_manager(self):
        """
        Render a workspace_manager.py file based on the scaffold and template.
        """
        # jinja2 template loader from the mulch sourcecode
        env = Environment(
            loader=PackageLoader("mulch", "templates"),
            autoescape=select_autoescape()
        )
        template = env.get_template(self.DEFAULT_WORKSPACE_TEMPLATE_FILENAME)

        rendered = template.render(
            project_name = self.project_name,
            scaffold=self.lock_data["scaffold"]
        ) # self.lock_data["scaffold"] is the scaffold dict loaded from the mulch-scaffold file

        logger.info(f"src lock_path = {self.manager_lock_path}")
        if self.manager_lock_path.exists():
            try:
                with open(self.manager_lock_path, "r", encoding="utf-8") as f:
                    existing = json.load(f)
                existing_scaffold = existing.get("scaffold", {})
                if existing_scaffold == self.lock_data["scaffold"]: #self.scaffold:
                    logging.debug(f"Scaffold unchanged. Skipping re-render of workspace_manager.py at {self.manager_path}")
                    typer.echo(f"Scaffold unchanged. Skipping re-render of workspace_manager.py.")
                    return False # 🛑 Skip rendering
                else:
                    if not typer.confirm(f"⚠️ Existing {self.manager_lock_path} does not match this scaffold structure."
                                         "Overwriting the workspace_manager.py file can break references for existing workspaces. Continue?",
                                         abort=True):
                        logger.info("User chose not to overwrite existing workspace_manager.py")
                        return False
                    else: 
                        pass # 🟢 Continue rendering
            except Exception as e:
                logger.warning(f"Could not read {self.manager_lock_path.name} for comparison: {e}")
                return False
        # Only reach here if:
        # 1. No lock file exists
        # 2. User confirmed overwrite
        # 3. Scaffolds match
        self.manager_path.parent.mkdir(parents=True, exist_ok=True)
        self.manager_path.write_text(rendered)
        with open(self.manager_lock_path, "w", encoding="utf-8") as f:
            json.dump(self.lock_data, f, indent=2)
        typer.echo(f"workspace_manager.py generated!")
        logging.debug(f"Generated workspace_manager.py at {self.manager_path}")
        return True # 🟢 Indicate that rendering was successful


def load_scaffold(target_dir: Path | None = None, strict_local_dotmulch:bool=False, seed_if_missing:bool=False) -> dict:
    target_dir = target_dir or Path.cwd()
    base = target_dir / ".mulch"

    if strict_local_dotmulch:
        # Only try .mulch — no fallback
        for fname in filenames:
            path = base / fname
            scaffold = try_load_scaffold_file(path)
            if scaffold:
                logger.info(f"✅ Loaded scaffold from: {path}")
                return scaffold

        if seed_if_missing:
            from mulch.seed_logic import write_seed_scaffold  # or wherever this lives
            logger.warning("⚠️ .mulch exists but no scaffold file found. Auto-seeding...")
            write_seed_scaffold(target_dir)
            return load_scaffold(target_dir, strict_local_dotmulch=True, seed_if_missing=False)

        raise FileNotFoundError("🚫 No valid `.mulch/mulch-scaffold.*` found and auto-seed not enabled.")

    # Default behavior: search all fallback paths
    
    base_dirs = [
        target_dir / ".mulch",    # 1. Local .mulch folder
        target_dir,               # 2. Root project dir
        Path.home() / 'mulch',               # 3. User root on system
        get_global_config_path(appname = "mulch") # 4. Global config
    ]
    
    filenames = ["mulch-scaffold.toml", "mulch-scaffold.json"]

    for base in base_dirs:
        for filename in filenames:
            path = base / filename
            scaffold = try_load_scaffold_file(path)
            if scaffold:
                logger.info(f"✅ Loaded scaffold from: {path}")
                return scaffold
            
    logger.warning("No valid scaffold file found. Falling back to internal scaffold.")
    return FALLBACK_SCAFFOLD

