# src/mulch/workspace_factory.py (project-agnostic, reusable)

import json
import logging
from pathlib import Path
from jinja2 import Environment, PackageLoader, select_autoescape #,FileSystemLoader
from mulch.helpers import get_global_config_path, get_user_root, try_load_scaffold_file

from mulch.constants import FALLBACK_SCAFFOLD, DEFAULT_SCAFFOLD_FILENAME
from mulch.logging_setup import setup_logging, setup_logging_portable
from mulch.workspace_status import WorkspaceStatus
from mulch.basepath_manager import PathContext

import typer
from importlib.resources import files

setup_logging_portable()
logger = logging.getLogger(__name__)


class WorkspaceFactory:
    f"""
    Project-agnostic workspace factory for use with the mulch CLI.
    Manages directory creation and standardized file placement based on {DEFAULT_SCAFFOLD_FILENAME}.
    Coming soon: generate a workspace_manager.py file in the src.
    """
    
    DEFAULT_WORKSPACE_CONFIG_FILENAME = "default-workspace.toml"
    DEFAULT_TEMPLATE_DIR = Path(__file__).parent / "templates"
    DEFAULT_WORKSPACE_TEMPLATE_FILENAME = "workspace_manager.py.j2"
    FALLBACK_SCAFFOLD = FALLBACK_SCAFFOLD # to make accessible, for pip and interally
    DEFAULT_SCAFFOLD_FILENAME = DEFAULT_SCAFFOLD_FILENAME # to make accessible, for pip and interally
    

    def __init__(self, base_path: Path, workspace_dir: Path, workspace_name: str, lock_data: dict, here=False, bare=False, stealth: bool = False):
        self.base_path = Path(base_path).resolve()
        self.workspace_name = workspace_name
        #self.workspace_dir = workspace_dir 
        #self.workspace_lock_path = self.workspace_dir / "workspace.lock"
        #self.manager_lock_path = self.base_path / "src" / self.base_path.name / "manager.lock"
        #self.manager_path = self.base_path / "src" / self.base_path.name / "workspace_manager.py"
        self.lock_data = lock_data
        self.here = here
        self.bare = bare
        self.stealth = stealth 
        self.context = PathContext(base_path, workspace_name, here=here, stealth=stealth)
        self.workspace_dir = self.context.workspace_dir 
        self.workspace_lock_path = self.context.workspace_lock_path
        self.manager_lock_path = self.context.manager_lock_path
        self.manager_path = self.context.manager_path 

        self.project_name = self.base_path.name # assumption that the target dir is the package name, fair enough

    def initialize(self, *, set_default: bool = True, here: bool = False, bare: bool = False):
        """
        Set up the workspace directories, default config, and emit status messages.
        This is a safe wrapper for post-instantiation setup.
        """
        self.check_and_create_workspace_dirs_from_scaffold(self.workspace_dir)
        typer.secho(f"Workspace '{self.workspace_name}' initialized at {self.workspace_dir}", fg=typer.colors.BRIGHT_MAGENTA)

        if set_default and not here and not bare:
            self.create_default_workspace_toml(self.workspace_dir, self.workspace_name)


    def get_path(self, key: str) -> Path:
        """
        Generic path getter using slash-separated key within the workspace.
        """
        path = self.workspace_dir
        for part in key.strip("/").split("/"):
            path /= part
        return path
    
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
                logging.warning(f"Failed to read {self.workspace_lock_path}: {e}")
                return WorkspaceStatus.DIFFERS
        else:
            return WorkspaceStatus.EXISTS_NO_LOCK
        

        
    def write_workspace_lockfile(self):
        
        with open(self.workspace_lock_path, "w", encoding="utf-8") as f:
            json.dump(self.lock_data, f, indent=2)
        logger.debug(f"Wrote lockfile to: {self.workspace_lock_path}")

    def seed_scaffolded_workspace_files(self):
        # no-op placeholder: future file seeding logic can go here
        pass
        
    @classmethod
    def determine_workspace_dir(cls, target_dir: Path, name: str, here: bool, bare: bool) -> Path:
        if here:
            return target_dir / name
        return target_dir / "workspaces" / name

    def check_and_create_workspace_dirs_from_scaffold(self, workspace_dir):
        """
        Create folders and files under the workspace directory as defined by the scaffold.
        """
        for parent, children in self.lock_data["scaffold"].items():
            base = workspace_dir / parent
            for child in children:
                path = base / child
                if "." in child:
                    if not path.exists():
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.touch()
                        logger.debug(f"Created file: {path}")
                else:
                    if not path.exists():
                        path.mkdir(parents=True, exist_ok=True)
                        logger.debug(f"Created folder: {path}")

    def initialize_full_workspace(self, set_default: bool = True):
        """
        One-shot method to create dirs, seed files, write lockfile, and optionally write default-workspace.toml
        """
        self.check_and_create_workspace_dirs_from_scaffold(self.workspace_dir)
        self.write_workspace_lockfile()
        if not self.here:
            self.render_workspace_manager()
            setup_logging()
        self.seed_scaffolded_workspace_files()
        if set_default and not self.here and not self.bare:
            self.create_default_workspace_toml(self.workspace_dir, self.workspace_name)

    @classmethod
    def create_default_workspace_toml(cls, workspaces_root: Path, workspace_name: str):
        """
        Write default-workspace.toml to the workspaces directory.
        """
        config_path = workspaces_root / cls.DEFAULT_WORKSPACE_CONFIG_FILENAME
        if not config_path.exists():
            config_path.write_text(f"[default-workspace]\nworkspace = \"{workspace_name}\"\n")
            logger.debug(f"Created {config_path}")
        else:
            logging.debug(f"{config_path} already exists; skipping overwrite")

    def seed_scaffolded_workspace_files(self):
        """
        Seed both static and templated workspace files.
        Call this after workspace creation.
        Seed only placeholder files that are already declared in scaffold and still empty.
        This ensures the scaffold drives structure, not the seeder.
        """
        self.seed_static_workspace_files()
        self.seed_templated_workspace_file()
        
    def seed_static_workspace_files(self):
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

    def seed_templated_workspace_file(self):
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

    def render_workspace_manager(self):
        """
        Render a workspace_manager.py file based on the scaffold and template.
        """

        if self.here or self.bare:
            typer.echo(f"No workspace_manager.py file necessary, skipping.")
        #env = Environment(loader=FileSystemLoader(self.DEFAULT_TEMPLATE_DIR))
        
        # jinja2 template loader from the mulch sourcecode
        env = Environment(
            loader=PackageLoader("mulch", "templates"),
            autoescape=select_autoescape()
        )
        template = env.get_template(self.DEFAULT_WORKSPACE_TEMPLATE_FILENAME)

        rendered = template.render(
            project_name = self.project_name,
            scaffold=self.lock_data["scaffold"],
            workspace_dir_name=self.workspace_name
        )


        
        #lock_path = output_dir / LOCK_FILE_NAME 
        logger.info(f"src lock_path = {self.manager_lock_path}")
        if self.manager_lock_path.exists():

            try:
                with open(self.manager_lock_path, "r", encoding="utf-8") as f:
                    
                    existing = json.load(f)
                existing_scaffold = existing.get("scaffold", {})
                if existing_scaffold == self.lock_data["scaffold"]: #self.scaffold:
                    logging.debug(f"Scaffold unchanged. Skipping re-render of workspace_manager.py at {self.manager_path}")
                    typer.echo(f"Scaffold unchanged. Skipping re-render of workspace_manager.py.")
                    return  # 🛑 Skip rendering
                else:
                    typer.confirm(f"⚠️ Existing {self.manager_lock_path} does not match this scaffold structure. Overwriting the workspace_manager.py file can break references for existing workspaces. Continue?", abort=True)
            except Exception as e:
                logging.warning(f"Could not read {self.manager_lock_path.name} for comparison: {e}")


        self.manager_path.parent.mkdir(parents=True, exist_ok=True)
        self.manager_path.write_text(rendered)
        with open(self.manager_lock_path, "w", encoding="utf-8") as f:
            json.dump(self.lock_data, f, indent=2)
        typer.echo(f"workspace_manager.py generated!")
        logging.debug(f"Generated workspace_manager.py at {self.manager_path}")

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
        get_global_config_path(appname = "mulch"), # 4. Global config
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

