# src/mulch/workspace_factory.py (project-agnostic, reusable)

import json
import logging
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

DEFAULT_SCAFFOLD_FILENAME = "scaffold.json"

class WorkspaceFactory:
    """
    Project-agnostic workspace factory for use with the mulch CLI.
    Manages directory creation and standardized file placement based on scaffold.json.
    Coming soon: generate a workspace_manager.py file in the src.
    """
    
    DEFAULT_WORKSPACE_CONFIG_FILENAME = "default-workspace.toml"
    DEFAULT_TEMPLATE_DIR = Path(__file__).parent / "templates"
    DEFAULT_TEMPLATE_FILENAME = "workspace_manager.py.j2"

    def __init__(self, base_path: Path, workspace_name: str):
        self.base_path = Path(base_path).resolve()
        self.workspace_name = workspace_name
        self.workspace_dir = self.base_path / "workspaces" / workspace_name
        self.scaffold = load_scaffold()

    def get_path(self, key: str) -> Path:
        """
        Generic path getter using slash-separated key within the workspace.
        """
        path = self.workspace_dir
        for part in key.strip("/").split("/"):
            path /= part
        return path

    def check_and_create_dirs_from_scaffold(self):
        """
        Create folders and files under the workspace directory as defined by the scaffold.
        """
        for parent, children in self.scaffold.items():
            base = self.workspace_dir / parent
            for child in children:
                path = base / child
                if "." in child:
                    if not path.exists():
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.touch()
                        logging.info(f"Created file: {path}")
                else:
                    if not path.exists():
                        path.mkdir(parents=True, exist_ok=True)
                        logging.info(f"Created folder: {path}")

    @classmethod
    def create_default_workspace_toml(cls, workspaces_root: Path, workspace_name: str):
        """
        Write default-workspace.toml to the workspaces directory.
        """
        config_path = workspaces_root / cls.DEFAULT_WORKSPACE_CONFIG_FILENAME
        if not config_path.exists():
            config_path.write_text(f"[default-workspace]\nworkspace = \"{workspace_name}\"\n")
            logging.info(f"Created {config_path}")
        else:
            logging.info(f"{config_path} already exists; skipping overwrite")

    def render_workspace_manager(self):
        """
        Render a workspace_manager.py file based on the scaffold and template.
        """
        env = Environment(loader=FileSystemLoader(self.DEFAULT_TEMPLATE_DIR))
        template = env.get_template(self.DEFAULT_TEMPLATE_FILENAME)

        project_name = self.base_path.name
        rendered = template.render(
            project_name = project_name,
            scaffold=self.scaffold,
            workspace_dir_name=self.workspace_name
        )

        src_dir = self.base_path / "src"  # <rootprojectname>/src
        output_dir = src_dir / project_name
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "workspace_manager.py"
        output_path.write_text(rendered)
        logging.info(f"Generated workspace_manager.py at {output_path}")

def load_scaffold(scaffold_path: Path | None = None) -> dict:
    if not scaffold_path:
        scaffold_path = Path(__file__).parent / DEFAULT_SCAFFOLD_FILENAME
    
    fallback_scaffold = {
        "": ["config", "data", "imports", "exports", "scripts", "secrets", "queries"],
        "exports": ["aggregate"],
        "config": ["default-workspace.toml"],
        "secrets": ["secrets.yaml", "secrets-example.yaml"],
        "queries": ["default-queries.toml"]
    }
    
    if not scaffold_path.exists():
        # File missing, log warning and return fallback
        print(f"Warning: Missing scaffold file: {scaffold_path}, using fallback scaffold.")
        return fallback_scaffold
        
    #with open(scaffold_path, "r") as f:
    #    return json.load(f)
        
    try:
        with open(scaffold_path, "r") as f:
            content = f.read().strip()
            if not content:
                print(f"Warning: Scaffold file {scaffold_path} is empty, using fallback scaffold.")
                return fallback_scaffold
            return json.loads(content)
    except json.JSONDecodeError as e:
        print(f"Warning: Scaffold file {scaffold_path} contains invalid JSON ({e}), using fallback scaffold.")
        return fallback_scaffold