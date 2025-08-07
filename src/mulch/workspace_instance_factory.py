# src/mulch/workspace_instance_factory.py (project-agnostic, reusable)

import json
import logging
from pathlib import Path
from jinja2 import Environment, PackageLoader, select_autoescape #,FileSystemLoader
import toml
import typer
from importlib.resources import files
from typing import Dict, Any, Optional

from mulch.helpers import get_global_config_path, get_user_root, try_load_scaffold_file
from mulch.constants import FALLBACK_SCAFFOLD, DEFAULT_SCAFFOLD_FILENAME
from mulch.logging_setup import setup_logging, setup_logging_portable
from mulch.flags_log_status import FlagsLockStatus
from mulch.workspace_status import WorkspaceStatus
from mulch.basepath_manager import PathContext


setup_logging_portable()
logger = logging.getLogger(__name__)


class WorkspaceInstanceFactory:
    """
    Project-agnostic workspace instance factory for use with the mulch CLI.
    Manages directory creation and standardized file placement based on scaffold definition.
    """
    
    DEFAULT_WORKSPACE_CONFIG_FILENAME = "default-workspace.toml"
    DEFAULT_TEMPLATE_DIR = Path(__file__).parent / "templates"
    DEFAULT_WORKSPACE_TEMPLATE_FILENAME = "workspace_manager.py.j2"
    FALLBACK_SCAFFOLD = FALLBACK_SCAFFOLD # to make accessible, for pip and interally
    DEFAULT_SCAFFOLD_FILENAME = DEFAULT_SCAFFOLD_FILENAME # to make accessible, for pip and interally
    

    def __init__(self, 
                 base_path: Path,
                 workspace_dir: Path,
                 workspace_name: str,
                 lock_data: dict,
                 *,
                 here: bool = False,
                 stealth: bool = False):
        """
        WorkspaceInstanceFactory.here is an attribute that references the setting of the --here flag, a flag of the command 'mulch workspace'. 
        When a workspace is generated, the value of self.here determines whether the workspace is generated in the root dir (if here is True, if the --here flag is used) or in root/workspaces/ (the default, if self.here is False, if the --here flag is not used.). 
        All workspaces should go in the same place for a given project. Ergo, to ensure this, a lock file should be set for the first workspace instance generated.
        
        Initialize a new workspace instance factory.
        
        Args:
            base_path: Root directory of the project
            workspace_dir: Directory where workspace will be created
            workspace_name: Name of the workspace
            lock_data: Scaffold and metadata for lockfile
            here: If True, create workspace in root instead of workspaces/
            stealth: If True, use .mulch/workspaces/ instead of root/workspaces/
        
        """
        self.base_path = Path(base_path).resolve()
        self.workspace_name = workspace_name
        self.lock_data = lock_data
        self.here = here
        self.stealth = stealth 
        
        # Create PathContext with explicit parameters
        self.context = PathContext(
            base_path=self.base_path,
            workspace_name=self.workspace_name,
            #workspace_dir=workspace_dir,
            here=self.here,
            stealth=self.stealth
        )

        # Get paths from context
        self.workspace_dir = self.context.workspace_dir 
        self.workspace_lock_path = self.context.workspace_lock_path
        self.flags_lock_path = self.context.flags_lock_path
        self.manager_lock_path = self.context.manager_lock_path
        self.manager_path = self.context.manager_path 

        self.project_name = self.base_path.name

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

    def evaluate_workspace_status(self) -> WorkspaceStatus:
        
        if not self.workspace_dir.exists():
            return WorkspaceStatus.MISSING

        if self.workspace_lock_path.exists():
            try:
                with open(self.workspace_lock_path, "r", encoding="utf-8") as f:
                    existing = json.load(f)
                existing_scaffold = existing.get("scaffold", {})
                if existing_scaffold == self.lock_data.get("scaffold", {}):
                    return WorkspaceStatus.MATCHES
                else:
                    return WorkspaceStatus.DIFFERS
            except Exception as e:
                logger.warning(f"Failed to read {self.workspace_lock_path}: {e}")
                return WorkspaceStatus.DIFFERS
        else:
            return WorkspaceStatus.EXISTS_NO_LOCK
        

        
    def write_workspace_lockfile(self) -> bool:
        
        with open(self.workspace_lock_path, "w", encoding="utf-8") as f:
            json.dump(self.lock_data, f, indent=2)
        logger.debug(f"Wrote lockfile to: {self.workspace_lock_path}")
    def write_workspace_lockfile(self):
        """Write workspace lock file after ensuring parent directory exists."""
        try:
            # Create workspace directory
            self.workspace_dir.mkdir(parents=True, exist_ok=True)
            
            # Write the lock file
            with open(self.workspace_lock_path, "w", encoding="utf-8") as f:
                json.dump(self.lock_data, f, indent=2)
            logger.debug(f"Wrote lockfile to: {self.workspace_lock_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to write workspace lock file: {e}")
            return False

    @classmethod
    def determine_workspace_dir(cls, target_dir: Path, name: str, here: bool, stealth: bool) -> Path:
        """
        Determine the workspace directory path based on flags.
        
        Args:
            target_dir: Base project directory
            name: Workspace name
            here: If True, create in current directory
            stealth: If True, use .mulch/workspaces/
        """
        if here:
            return target_dir / name
        if stealth:
            return target_dir / ".mulch" / "workspaces" / name
        return target_dir / "workspaces" / name
    
    def check_and_create_workspace_dirs_from_scaffold(self, workspace_dir: Path) -> None:
        """
        Create workspace directory structure from arbitrarily nested scaffold definition.
        
        Expected TOML structure:
        [scaffold]
        dirs = [
            "data",
            "data/raw",
            "data/processed/monthly",
            "queries/historical/archive",
        ]
        files = [
            "queries/historical/default-queries.toml",
            "data/processed/monthly/README.md",
            "secrets/secrets-example.yaml"
        ]
        """
        scaffold_data = self.lock_data.get("scaffold", {})
        if "scaffold" in scaffold_data:  # Handle double-nested case from your TOML
            scaffold_data = scaffold_data["scaffold"]

        # Handle directory creation first
        if "dirs" in scaffold_data:
            for dir_path in scaffold_data["dirs"]:
                full_path = workspace_dir / dir_path
                if not full_path.exists():
                    full_path.mkdir(parents=True, exist_ok=True)
                    logger.debug(f"Created directory: {full_path}")
        
        # Handle file creation second (ensures parent dirs exist)
        if "files" in scaffold_data:
            for file_path in scaffold_data["files"]:
                full_path = workspace_dir / file_path
                if not full_path.exists():
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    full_path.touch()
                    logger.debug(f"Created file: {full_path}")

        # Handle alternative nested dict format if present
        if "structure" in scaffold_data:
        #if isinstance(scaffold_data.get("structure", {}), dict):
            def create_nested_structure(parent_path: Path, structure: dict) -> None:
                """Recursively create nested directory structure"""
                for name, content in structure.items():
                    current_path = parent_path / name
                    
                    if isinstance(content, dict):
                        # It's a directory with nested content
                        current_path.mkdir(parents=True, exist_ok=True)
                        logger.debug(f"Created directory: {current_path}")
                        create_nested_structure(current_path, content)
                    elif isinstance(content, list):
                        # It's a directory with list of files/dirs
                        current_path.mkdir(parents=True, exist_ok=True)
                        logger.debug(f"Created directory: {current_path}")
                        for item in content:
                            item_path = current_path / item
                            if "." in item:  # Basic file detection
                                item_path.parent.mkdir(parents=True, exist_ok=True)
                                item_path.touch()
                                logger.debug(f"Created file: {item_path}")
                            else:
                                item_path.mkdir(parents=True, exist_ok=True)
                                logger.debug(f"Created directory: {item_path}")
                    elif content is None or content == "":
                        # It's an empty directory
                        current_path.mkdir(parents=True, exist_ok=True)
                        logger.debug(f"Created empty directory: {current_path}")
                    else:
                        # Assume it's a file
                        current_path.parent.mkdir(parents=True, exist_ok=True)
                        current_path.touch()
                        logger.debug(f"Created file: {current_path}")
            
            create_nested_structure(workspace_dir, scaffold_data["structure"])

        logger.info(f"Completed workspace scaffold creation in {workspace_dir}")

    def create_workspace(self, *, set_default: bool = True) -> None:
        """
        Create a new workspace with scaffold structure and configuration.
        
        Args:
            set_default: Whether to set this as the default workspace (ignored if --here flag was used)
        """
        # Check workspace status first
        status = self.evaluate_workspace_status()
        if status != WorkspaceStatus.MISSING:
            logger.warning(f"Workspace already exists with status: {status}")
            return

        # Create the workspace structure
        self.write_workspace_lockfile()
        self.check_and_create_workspace_dirs_from_scaffold(self.workspace_dir)
        self.build_scaffolded_workspace_files()

        # Handle default workspace setting
        if set_default and not self.here:
            self.create_default_workspace_toml(self.workspace_dir.parent, self.workspace_name)
        
        typer.secho(f"✨ Workspace '{self.workspace_name}' created at {self.workspace_dir}", 
                    fg=typer.colors.BRIGHT_MAGENTA)

    
    @classmethod
    def create_default_workspace_toml(cls, workspaces_root: Path, workspace_name: str) -> None:
        """
        Write default-workspace.toml to the workspaces directory.
        
        Args:
            workspaces_root: Directory containing all workspaces (usually 'workspaces/')
            workspace_name: Name of the workspace to set as default
        """
        config_path = workspaces_root / cls.DEFAULT_WORKSPACE_CONFIG_FILENAME
        if not config_path.exists():
            config_path.write_text(f"[default-workspace]\nworkspace = \"{workspace_name}\"\n")
            logger.debug(f"Created {config_path}")
        else:
            logging.debug(f"{config_path} already exists; skipping overwrite")

    def build_scaffolded_workspace_files(self) -> None:
        """
        Seed both static and templated workspace files.
        Call this after workspace creation.
        Seed only placeholder files that are already declared in scaffold and still empty.
        This ensures the scaffold drives structure, not the seeder.
        """
        self.build_static_workspace_files()
        self.build_templated_workspace_files()
        
    def build_static_workspace_files(self) -> None:
        """
        Populate essential workspace files *only if* their placeholder files already exist.
        Avoids introducing files/folders not declared in the scaffold.
        """
        seed_map = {
            Path("secrets") / "secrets-example.yaml": "secrets-example.yaml",
            Path("queries") / "default-queries.toml": "default-queries.toml",
        }

        for rel_path, src_filename in seed_map.items():
            dest = self.workspace_dir / rel_path
            # Clarify that seeders depend on placeholders
            if dest.exists() and dest.stat().st_size == 0:
                try:
                    src = files("mulch") / src_filename
                    with src.open("r", encoding="utf-8") as f_in:
                        contents = f_in.read()
                    dest.write_text(contents, encoding="utf-8")
                    logger.debug(f"Seeded workspace file: {dest}")
                    typer.echo(f"Seeded workspace file: {dest.name}")
                except Exception as e:
                    logger.warning(f"Failed to seed {rel_path}: {e}")
            else:
                logger.debug(f"Skipped seeding {dest}; file doesn't exist or is not empty.")

    def build_templated_workspace_files(self):
        """
        Generate helpful default files in the new workspace, such as about_this_workspace.md.
        """
        workspace_dir = self.workspace_dir

        env = Environment(
            loader=PackageLoader("mulch", "templates"),
            autoescape=select_autoescape()
        )

        about_path = workspace_dir / "about_this_workspace.md"

        if not about_path.exists():
            try:
                template = env.get_template("about_this_workspace.md.j2")
                content = template.render(
                    workspace_name=self.workspace_name,
                    generated_at=self.lock_data.get("generated_at", ""),
                    scaffold_source=self.lock_data.get("generated_by", "")
                )
                about_path.write_text(content, encoding="utf-8")
            except Exception as e:
                logger.warning(f"Failed to render about_this_workspace.md from template: {e}")
                content = f"# About {self.workspace_name}\n\nGenerated on {self.lock_data.get('generated_at', '')}"
            logging.debug(f"Seeded {about_path}")
        else:
            logging.debug(f"{about_path} already exists; skipping")


def load_scaffold_(scaffold_path: Path | None = None) -> dict:
    if not scaffold_path:
        scaffold_path = Path(__file__).parent / DEFAULT_SCAFFOLD_FILENAME
    
    if not scaffold_path.exists():
        # File missing, log warning and return fallback
        typer.echo(f"Missing scaffold file, using fallback scaffold.")
        logger.debug(f"Warning: Missing scaffold file: {scaffold_path}, using fallback scaffold.")
        return FALLBACK_SCAFFOLD
        
    #with open(scaffold_path, "r") as f:
    #    return json.load(f)
        
    try:
        with open(scaffold_path, "r") as f:
            content = f.read().strip()
            if not content:
                logger.debug(f"Warning: Scaffold file {scaffold_path} is empty, using fallback scaffold.")
                typer.echo(f"Scaffold file is empty, using fallback scaffold.")
                return FALLBACK_SCAFFOLD
            return json.loads(content)
    except json.JSONDecodeError as e:
        logger.warning(f"Warning: Scaffold file {scaffold_path} contains invalid JSON ({e}), using fallback scaffold.")
        return FALLBACK_SCAFFOLD

def load_scaffold__(target_dir: Optional[Path] = None, 
                  strict_local_dotmulch:bool=False, 
                  seed_if_missing:bool=False) -> Dict[str, Any]:
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

# Move outside class
def load_scaffold(
    target_dir: Optional[Path] = None, 
    strict_local_dotmulch: bool = False,
    seed_if_missing: bool = False
) -> Dict[str, Any]:
    """
    Load scaffold configuration from various possible locations.
    
    Args:
        target_dir: Directory to start searching from (defaults to cwd)
        strict_local_dotmulch: If True, only look in .mulch directory
        seed_if_missing: If True and strict mode, create seed scaffold
    
    Returns:
        Dict containing scaffold configuration
    
    Raises:
        FileNotFoundError: If strict mode and no scaffold found
    """
    target_dir = target_dir or Path.cwd()
    base = target_dir / ".mulch"

    filenames = ["mulch-scaffold.toml", "mulch-scaffold.json"]

    if strict_local_dotmulch:
        # ...existing strict mode code...
        pass

    # Default behavior: search all fallback paths
    base_dirs = [
        target_dir / ".mulch",    # 1. Local .mulch folder
        target_dir,               # 2. Root project dir
        Path.home() / 'mulch',    # 3. User root on system
        get_global_config_path(appname="mulch")  # 4. Global config
    ]

    for base in base_dirs:
        for filename in filenames:
            path = base / filename
            scaffold = try_load_scaffold_file(path)
            if scaffold:
                logger.info(f"📄 Loaded scaffold from: {path}")
                return scaffold
            
    logger.warning("No valid scaffold file found. Using fallback scaffold.")
    return FALLBACK_SCAFFOLD