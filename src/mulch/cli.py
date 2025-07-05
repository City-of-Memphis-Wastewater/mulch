# src/mulch/cli.py

import typer
import json
from pathlib import Path
import logging
#from pprint import pprint

from mulch.workspace_factory import WorkspaceFactory
#from mulch.logging_setup import setup_logging

#import logging.config

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

HELP_TEXT = "Mulch CLI for scaffolding Python project workspaces."
SCAFFOLD_FILE_PREPPED = 'scaffold.json'

app = typer.Typer(help=HELP_TEXT, no_args_is_help=True)

# load the fallback_scaffold to this file
wf = WorkspaceFactory(Path.cwd(),'placeholder_workspace_name',{'placeholder_scaffold_dict'})
FALLBACK_SCAFFOLD = wf.FALLBACK_SCAFFOLD




@app.callback()
def main():
    """
    {{ HELP_TEXT }}
    """
    pass


def _init_workspace(target_dir: Path, name: str, scaffold_structure: dict, set_default: bool) -> WorkspaceFactory:
    """
    Shared internal logic to scaffold workspace directories.
    """
    target_dir = target_dir.resolve()
    wf = WorkspaceFactory(base_path=target_dir, workspace_name=name, scaffold_structure=scaffold_structure)
    wf.check_and_create_dirs_from_scaffold()

    if set_default:
        wf.create_default_workspace_toml(target_dir / "workspaces", name)

    return wf


def _render_workspace_manager(target_dir: Path, scaffold_structure: dict):
    """
    Shared internal logic to render workspace_manager.py.
    """
    wf = WorkspaceFactory(base_path=target_dir, workspace_name="placeholder_workspace_name", scaffold_structure=scaffold_structure)
    wf.render_workspace_manager()
    return

def _establish_software_elements(target_dir: Path):
    print("auto generate logs dir in root please")
    print("auto generate config dir in root please")

@app.command()
def init(
    target_dir: Path = typer.Argument(Path.cwd(), help="Target project root (defaults to current directory)."),
    name: str = typer.Option("default", "--name", "-n", help="Name of the workspace to create."),
    #scaffold_structure: str = typer.Option(json.dumps(FALLBACK_SCAFFOLD), "--scaffold", "-s", help="Scaffold structure to determine the folder hierarchy for each workspace."),
    #scaffold_filepath: str = typer.Option(Path.cwd() / 'scaffold.json', "--filepath", "-f", help="File holding scaffold structure to determine the folder hierarchy for each workspace."),
    scaffold_filepath: str = typer.Option(None, "--filepath", "-f", help="File holding scaffold structure to determine the folder hierarchy for each workspace."),
    set_default: bool = typer.Option(True, "--set-default/--no-set-default", help="Write default-workspace.toml")
):
    """
    Initialize a new workspace folder tree using scaffold.json or fallback.
    """

    if scaffold_filepath:
        with open(scaffold_filepath, "r", encoding="utf-8") as f:
            scaffold_dict = json.load(f)
    elif Path(SCAFFOLD_FILE_PREPPED).is_file(): # check current directory for the prepped filename
        with open(SCAFFOLD_FILE_PREPPED, "r", encoding="utf-8") as f:
            scaffold_dict = json.load(f)
    elif (Path.cwd() / SCAFFOLD_FILE_PREPPED).is_file(): # check current directory for the prepped filename
        with open(Path.cwd() / SCAFFOLD_FILE_PREPPED, "r", encoding="utf-8") as f:
            scaffold_dict = json.load(f)
    else:
        scaffold_dict = FALLBACK_SCAFFOLD
    wf = _init_workspace(target_dir, name, scaffold_dict, set_default)
    _render_workspace_manager(target_dir, scaffold_dict)
    _establish_software_elements(target_dir)
    typer.echo(f"Workspace '{name}' initialized at {wf.workspace_dir}")
"""
@app.command("render")
def render(
    target_dir: Path = typer.Argument(Path.cwd(), help="Target project root (where scaffold.json lives)."),
    scaffold_structure: str = typer.Argument(json.dumps(FALLBACK_SCAFFOLD), help=f"Scaffold dictionary, load from file or build the dictionary. FALLBACK_SCAFFOLD = {FALLBACK_SCAFFOLD}")
    ):
    '''
    Render workspace_manager.py using scaffold.json and a Jinja2 template.
    '''
    scaffold_dict = json.loads(scaffold_structure)
    _render_workspace_manager(target_dir, scaffold_dict)
"""

@app.command()
def prep(
    target_dir: Path = typer.Argument(Path.cwd(), help="Target project root (defaults to current directory)."),
    filename: str = typer.Option('scaffold.json',"--filename","-f",help = "Scaffold filename (defaults to 'scaffold.json')"),
    scaffold_structure: str = typer.Option(None, "--scaffold", "-s", help = "Provide the scaffold hierarchy structure dictionary as text, to write to file. Defaulst to the FALLBACK_SCAFFOLD.")
    ):
    f"""
    
    Use single quotes to capture the internal double quotes from 'mulch show':

    mulch show:
        {FALLBACK_SCAFFOLD}
    Powershell:
        $scaffold_str | Out-File -Encoding utf8 -FilePath scaffold-temp.json

    """
    if not scaffold_structure:
        scaffold_dict = FALLBACK_SCAFFOLD
    else:
        scaffold_dict = json.loads(scaffold_structure)
    full_path = target_dir / filename
    SCAFFOLD_FILE_PREPPED = full_path
    full_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
    
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(scaffold_dict, f, indent=2)
    
    typer.echo(f"✅ Wrote scaffold to: {full_path}")

@app.command()
def show(
    filepath: Path = typer.Option(
        None, "--filepath", "-f", help="Path to a scaffold JSON file."
    ),
    use_default: bool = typer.Option(
        False, "--use-default", "-d", help="Use default scaffold.json from CWD."
    ),
    ):
    """
    Display the fallback scaffold dictionary structure or load and display a scaffold JSON file.
    """
    if filepath:
        with open(filepath, "r", encoding="utf-8") as f:
            scaffold = json.load(f)
    elif use_default:
        default_path = Path.cwd() / "scaffold.json"
        if not default_path.exists():
            typer.echo(f"Default file not found at {default_path}.")
            raise typer.Exit(code=1)
        with open(default_path, "r", encoding="utf-8") as f:
            scaffold = json.load(f)
    else:
        scaffold = FALLBACK_SCAFFOLD
    
    typer.echo(json.dumps(scaffold, indent=2))
    #pprint(scaffold)
if __name__ == "__main__":
    app()
