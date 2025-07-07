# src/mulch/workspace_factory.py (project-agnostic, reusable)

import json
import logging
from pathlib import Path
from jinja2 import Environment, PackageLoader, select_autoescape #,FileSystemLoader

import typer
from importlib.resources import files

from mulch.logging_setup import setup_logging_portable


setup_logging_portable()
logger = logging.getLogger(__name__)

DEFAULT_SCAFFOLD_FILENAME = "mulch-scaffold.json"
LOCK_FILE_NAME = 'mulch.lock'
FALLBACK_SCAFFOLD = {
        "": ["config", "docs", "imports", "exports", "scripts", "secrets", "queries","about_this_workspace.md"],
        "exports": ["aggregate"],
        "config": ["default-workspace.toml", "logging.json"],
        "secrets": ["secrets-example.yaml"],
        "queries": ["default-queries.toml"]
    }

class WorkspaceFactory:
    f"""
    Project-agnostic workspace factory for use with the mulch CLI.
    Manages directory creation and standardized file placement based on {DEFAULT_SCAFFOLD_FILENAME}.
    Coming soon: generate a workspace_manager.py file in the src.
    """
    
    DEFAULT_WORKSPACE_CONFIG_FILENAME = "default-workspace.toml"
    DEFAULT_TEMPLATE_DIR = Path(__file__).parent / "templates"
    DEFAULT_TEMPLATE_FILENAME = "workspace_manager.py.j2"
    FALLBACK_SCAFFOLD = FALLBACK_SCAFFOLD # to make accessible, for pip and interally
    DEFAULT_SCAFFOLD_FILENAME = DEFAULT_SCAFFOLD_FILENAME # to make accessible, for pip and interally

    def __init__(self, base_path: Path, workspace_dir: Path, workspace_name: str, lock_data: dict):
        self.base_path = Path(base_path).resolve()
        self.workspace_name = workspace_name
        self.workspace_dir = workspace_dir 
        self.lock_data = lock_data

    def get_path(self, key: str) -> Path:
        """
        Generic path getter using slash-separated key within the workspace.
        """
        path = self.workspace_dir
        for part in key.strip("/").split("/"):
            path /= part
        return path

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
        #env = Environment(loader=FileSystemLoader(self.DEFAULT_TEMPLATE_DIR))
        
        env = Environment(
            loader=PackageLoader("mulch", "templates"),
            autoescape=select_autoescape()
        )


        template = env.get_template(self.DEFAULT_TEMPLATE_FILENAME)

        project_name = self.base_path.name
        rendered = template.render(
            project_name = project_name,
            scaffold=self.lock_data["scaffold"],
            workspace_dir_name=self.workspace_name
        )

        src_dir = self.base_path / "src"  # <rootprojectname>/src
        output_dir = src_dir / project_name
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "workspace_manager.py"
        lock_path = output_dir / LOCK_FILE_NAME
        
        if lock_path.exists():
            try:
                with open(lock_path, "r", encoding="utf-8") as f:
                    
                    existing = json.load(f)
                existing_scaffold = existing.get("scaffold", {})
                if existing_scaffold == self.lock_data["scaffold"]: #self.scaffold:
                    logging.debug(f"Scaffold unchanged. Skipping re-render of workspace_manager.py at {output_path}")
                    typer.echo(f"Scaffold unchanged. Skipping re-render of workspace_manager.py.")
                    return  # 🛑 Skip rendering
                else:
                    typer.confirm(f"⚠️ Existing {LOCK_FILE_NAME} does not match this scaffold structure. Continue?", abort=True)
            except Exception as e:
                logging.warning(f"Could not read {LOCK_FILE_NAME} for comparison: {e}")

        # ✅ Check for overwrite *here*, not in CLI
        if output_path.exists():
            typer.confirm(
                f"⚠️ A workspace_manager.py file already exists at {output_path}. "
                f"Overwriting it may break existing tooling. Continue?",
                abort=True
            )
            
        output_path.write_text(rendered)
        with open(lock_path, "w", encoding="utf-8") as f:
            json.dump(self.lock_data, f, indent=2)
        typer.echo(f"workspace_manager.py generated!")
        logging.debug(f"Generated workspace_manager.py at {output_path}")

def load_scaffold(scaffold_path: Path | None = None) -> dict:
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