# src/mulch/cli.py

import typer
import json
from pathlib import Path
import logging
import datetime
from importlib.metadata import version, PackageNotFoundError

from mulch.decorators import with_logging
from mulch.workspace_factory import WorkspaceFactory
from mulch.logging_setup import setup_logging, setup_logging_portable

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

HELP_TEXT = "Mulch CLI for scaffolding Python project workspaces."
DEFAULT_SCAFFOLD_FILENAME = 'mulch-scaffold.json'
LOCK_FILE_NAME = 'mulch.lock'
try:
    MULCH_VERSION = version("mulch")
except PackageNotFoundError:
    MULCH_VERSION = "unknown"
# load the fallback_scaffold to this file
wf = WorkspaceFactory(Path.cwd(),'placeholder_workspace_name',{})
FALLBACK_SCAFFOLD = wf.FALLBACK_SCAFFOLD

# Create the Typer CLI app
app = typer.Typer(help=HELP_TEXT, no_args_is_help=True, add_completion=False)

@app.callback()
def main(
    version: bool = typer.Option(None, "--version", callback=lambda v: print_version(v), is_eager=True, help="Show the version and exit.")
):
    """
    Mulch CLI for scaffolding Python project workspaces
    """

def print_version(value: bool):
    if value:
        try:
            typer.echo(f"mulch {MULCH_VERSION}")
        except PackageNotFoundError:
            typer.echo("Version info not found")
        raise typer.Exit()

def _should_generate_workspace(workspace_dir: Path, lock_data: dict) -> bool:
    lock_path = workspace_dir / LOCK_FILE_NAME

    if workspace_dir.exists():
        if lock_path.exists():
            with open(lock_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
            existing_scaffold = existing.get("scaffold", {})
            if existing_scaffold == lock_data["scaffold"]:
                typer.echo("✅ Scaffold matches existing scaffold.lock. Skipping workspace generation.")
                return False
            else:
                typer.confirm(
                    f"⚠️ {LOCK_FILE_NAME} exists and differs from current scaffold submission.\n"
                    f"Overwrite workspace?",
                    abort=True
                )
        else:
            typer.confirm(
                f"⚠️ Workspace directory {workspace_dir} exists but no {LOCK_FILE_NAME} was found.\n"
                f"Overwrite workspace?",
                abort=True
            )
    return True

def _init_workspace(target_dir: Path, name: str, lock_data: dict, set_default: bool) -> WorkspaceFactory:
    """
    Shared internal logic to scaffold workspace directories.
    """
    target_dir = target_dir.resolve()
    wf = WorkspaceFactory(base_path=target_dir, workspace_name=name, lock_data = lock_data)
    wf.check_and_create_workspace_dirs_from_scaffold()
    typer.echo(f"Workspace '{name}' initialized at {wf.workspace_dir}")

    if set_default:
        wf.create_default_workspace_toml(target_dir / "workspaces", name)

    return wf

def _generate_workspace_lockfile(workspace_dir : Path, lock_data):
    lock_path = workspace_dir / LOCK_FILE_NAME
    logger.debug(f"lock_path = {lock_path}")
    if lock_path.exists():
        with open(lock_path, "r", encoding="utf-8") as f:
            existing = json.load(f)
        existing_scaffold = existing.get("scaffold", {})
        if existing_scaffold != lock_data["scaffold"]:
            #typer.echo(f"existing_scaffold = {existing_scaffold}")
            #typer.echo(f"lock_data = {lock_data}")
            typer.confirm(
                f"⚠️ {LOCK_FILE_NAME} already exists at {lock_path}, but the scaffold structure has changed.\n"
                f"Overwriting may cause incompatibility with this workspace.\n"
                f"Continue?",
                abort=True
            )

    with open(lock_path, "w", encoding="utf-8") as f:
        json.dump(lock_data, f, indent=2)
    logger.info(f"Wrote {LOCK_FILE_NAME} to {lock_path}")

def _render_workspace_manager(target_dir: Path, lock_data: dict):
    """
    Shared internal logic to render workspace_manager.py.
    """
        
    wf = WorkspaceFactory(base_path=target_dir, workspace_name="placeholder_workspace_name", lock_data = lock_data)
    wf.render_workspace_manager()
    return

def _establish_software_elements(target_dir: Path):
    pass

@app.command()
@with_logging
def init(
    target_dir: Path = typer.Argument(Path.cwd(), help="Target project root (defaults to current directory)."),
    name: str = typer.Option("default", "--name", "-n", help="Name of the workspace to create."),
    scaffold_filepath: str = typer.Option(None, "--filepath", "-f", help="File holding scaffold structure to determine the folder hierarchy for each workspace."),
    set_default: bool = typer.Option(True, "--set-default/--no-set-default", help="Write default-workspace.toml")
):
    """
    Initialize a new workspace folder tree, using the mulch-scaffold.json structure or the fallback structure embedded in WorkspaceFactory.
    Build the workspace_manager.py file in the source code.
    Establish a logs folder at root, with the logging.json file.
    """

    scaffold_dict = None

    if scaffold_filepath:
        with open(scaffold_filepath, "r", encoding="utf-8") as f:
            scaffold_dict = json.load(f)
        logger.info(f"Scaffold loaded from explicitly provided file: {scaffold_filepath}")

    else:
        default_scaffold_path = target_dir / DEFAULT_SCAFFOLD_FILENAME
        if default_scaffold_path.is_file():
            with open(default_scaffold_path, "r", encoding="utf-8") as f:
                scaffold_dict = json.load(f)
            logger.info(f"Scaffold loaded from {default_scaffold_path}")
        else:
            scaffold_dict = FALLBACK_SCAFFOLD
            logger.info("Scaffold loaded from embedded fallback structure (FALLBACK_SCAFFOLD)")

    lock_data = {
        "scaffold": scaffold_dict,
        "generated_by": f"mulch {MULCH_VERSION}",
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    
    workspace_dir = target_dir / "workspaces" / name
    
    if _should_generate_workspace(workspace_dir, lock_data):
        wf = _init_workspace(target_dir, name, lock_data, set_default)
        _generate_workspace_lockfile(workspace_dir, lock_data)
        _render_workspace_manager(target_dir, lock_data)
        _establish_software_elements(target_dir)
        wf.seed_scaffolded_workspace_files()
    else:
        typer.echo(f"Workspace '{name}' already exists and is up-to-date with the scaffold.")


@app.command()
#@with_logging(use_portable=True)
def file(
    target_dir: Path = typer.Argument(Path.cwd(), help="Target project root (defaults to current directory)."),
    filepath_in: str = typer.Option(None,"--filepath-in","-i",help = "Exsting scaffold filename that you want copied. You must use -o/--filepath-out in conjunction with -i/--filepath-in"),
    use_embedded: bool = typer.Option(
        False, "--use-embedded-fallback-structure", "-e", help="Reference the embedded structure FALLBACK_SCAFFOLD."
    ),
    ):
    """

    Drop a scaffold file to disk, at the target directory.
    The default is the fallback embedded scaffold structure.
    You are able to edit this file manually.  

    Alternatively, you can use the 'show' command. 
    Example PowerShell snippet:
        mulch show -c
        $scaffold_str = '{"": ["config", "data", ...]}'
        $scaffold_str | Out-File -Encoding utf8 -FilePath mulch-scaffold.json
    """
    
    scaffold_path = target_dir / DEFAULT_SCAFFOLD_FILENAME
    scaffold_dict = FALLBACK_SCAFFOLD
    if use_embedded:
        pass # scaffold_dict = FALLBACK_SCAFFOLD
    elif filepath_in:
        with open(filepath_in, "r", encoding="utf-8") as f:
            scaffold_dict = json.load(f)

    if scaffold_path.exists():
        if not typer.confirm(f"⚠️ {scaffold_path} already exists. Overwrite?"):
            typer.echo("Aborted: Did not overwrite existing scaffold file.")
            raise typer.Abort()
    with open(scaffold_path, "w", encoding="utf-8") as f:
        json.dump(scaffold_dict, f, indent=2)
    
    typer.echo(f"✅ Wrote scaffold to: {scaffold_path}")
    typer.echo("✏️  You can now manually edit this file to customize your workspace layout.")
    typer.echo("⚙️  Changes to this scaffold file will directly affect the workspace layout and the generated workspace_manager.py when you run 'mulch init'.")


@app.command()
def show(
    filepath: Path = typer.Option(
        None, "--filepath", "-f", help="Path to an explicit scaffold JSON file."
    ),
    use_default: bool = typer.Option(
        False, "--use-default-filepath", "-d", help=f"Reference the default filepath .\{DEFAULT_SCAFFOLD_FILENAME}."
    ),
    use_embedded: bool = typer.Option(
        False, "--use-embedded-fallback-structure", "-e", help="Reference the embedded structure FALLBACK_SCAFFOLD."
    ),
    collapsed: bool = typer.Option(
        False, "--collapsed-print", "-c", help="Show the hard-to-read but easy-to-copy-paste version."
    ),
    ):
    """
    Display the fallback scaffold dictionary structure or load and display a scaffold JSON file.
    """
    default_path = Path.cwd() / DEFAULT_SCAFFOLD_FILENAME

    if filepath:
        if not filepath.exists():
            typer.echo(f"File not found at {filepath}.")
            typer.echo(f"Recommendation: use the default file (show -d) or the fallback scaffold (show -e)")
            raise typer.Exit(code=1)
        with open(filepath, "r", encoding="utf-8") as f:
            scaffold = json.load(f)
        logger.info(f"Structure pulled from the provided filepath: {filepath}")
    elif use_default:
        if not default_path.exists():
            typer.echo(f"Default file not found at {default_path}.")
            typer.echo(f"Recommendation: use an explicit file (show -f [FILEPATH]) or the fallback scaffold (show -e)")
            raise typer.Exit(code=1)
        with open(default_path, "r", encoding="utf-8") as f:
            scaffold = json.load(f)
        logger.info(f"Structure pulled from the default filepath: {default_path}")
    elif use_embedded:
        scaffold = FALLBACK_SCAFFOLD
        logger.info(f"Structure pulled from the FALLBACK_SCAFFOLD embedded in workspace_factory.py.")
    else:
        if default_path.exists():
            with open(default_path, "r", encoding="utf-8") as f:
                scaffold = json.load(f)
                logger.info(f"Structure pulled from the default filepath: {default_path}")
        else:
            scaffold = FALLBACK_SCAFFOLD
            logger.info(f"Structure pulled from the FALLBACK_SCAFFOLD embedded in workspace_factory.py.")
    
    print("\n")
    if collapsed:
        typer.echo(json.dumps(scaffold, separators=(",", ":")))
    else:
        typer.echo(json.dumps(scaffold, indent=2))
    
if __name__ == "__main__":
    app()
