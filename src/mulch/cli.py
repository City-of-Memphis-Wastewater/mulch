# src/mulch/cli.py

import typer
import json
import toml
from pathlib import Path
import logging
import datetime
from importlib.metadata import version, PackageNotFoundError
import subprocess
from pprint import pprint

from mulch.decorators import with_logging
from mulch.workspace_factory import WorkspaceFactory, load_scaffold
from mulch.logging_setup import setup_logging, setup_logging_portable
from mulch.helpers import open_editor, calculate_nowtime_foldername, resolve_scaffold, get_global_config_path, resolve_first_existing_path, get_username_from_home_directory
from mulch.commands.dotfolder import create_dot_mulch
from mulch.constants import FALLBACK_SCAFFOLD, LOCK_FILE_NAME, DEFAULT_SCAFFOLD_FILENAME
from mulch.workspace_status import WorkspaceStatus
from mulch.scaffold_loader import load_scaffold_file


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


HELP_TEXT = "Mulch CLI for scaffolding Python project workspaces."
SCAFFOLD_TEMPLATES_FILENAME = 'mulch-scaffold-template-dictionary.toml'

FILENAMES_OF_RESPECT = [
    'mulch-scaffold.toml',
    'mulch-scaffold.json'
]

# Paths are checked in order of respect for loading the scaffold template dictionary.
# These are used when running `mulch file`, `mulch show`, or any command needing layout templates.
ORDER_OF_RESPECT = [
    Path('.mulch'),
    Path('.'),
    Path.home() / 'mulch'#,
    #get_global_config_path(appname="mulch")
]
maybe_global = get_global_config_path(appname="mulch")
if maybe_global:
    ORDER_OF_RESPECT.append(Path(maybe_global))

TEMPLATE_CHOICE_DICTIONARY_FILEPATHS = [
    p / SCAFFOLD_TEMPLATES_FILENAME
    for p in ORDER_OF_RESPECT
    if isinstance(p, Path)
]


try:
    MULCH_VERSION = version("mulch")
    __version__ = version("mulch")
except PackageNotFoundError:
    MULCH_VERSION = "unknown"

try:
    from importlib.metadata import version
    __version__ = version("mulch")
except PackageNotFoundError:
    # fallback if running from source
    try:
        with open(Path(__file__).parent / "VERSION") as f:
            __version__ = f.read().strip()
    except FileNotFoundError:
        __version__ = "dev"
    
# load the fallback_scaffold to this file

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
            typer.secho(f"mulch {MULCH_VERSION}",fg=typer.colors.GREEN, bold=True)
        except PackageNotFoundError:
            typer.echo("Version info not found")
        raise typer.Exit()

def _determine_workspace_dir(target_dir, name, here, stealth: bool = False) -> Path:
    if stealth:
        return target_dir / name
    if not here:
        workspace_dir = target_dir / "workspaces" / name
    elif here:
        workspace_dir = target_dir / name
    return workspace_dir # type: ignore


def _establish_software_elements(target_dir: Path):
    pass

def _all_order_of_respect_failed(order_of_respect):
    failed = True
    for path in order_of_respect:
        if Path(path).exists():
            failed = False
    return failed

def make_dot_mulch_folder(target_dir):
    return create_dot_mulch(target_dir, order_of_respect=ORDER_OF_RESPECT)

def make_dot_mulch_folder_(target_dir):
    dot_mulch_folder = Path(target_dir) / '.mulch'
    if not dot_mulch_folder.exists():
        if False:
            dot_mulch_folder.mkdir()
            # this isn't good enough
            # it should run the logic for `mulch folder` instead, which includes templates, to the most available fallback, which ironically requires checking the list of order_or_respect
        else:
            # hack
            command = ["mulch", "folder"]
            return subprocess.call(command) == 0  # True if ping succeeds
        
@app.command()
@with_logging
def init(
    target_dir: Path = typer.Option(Path.cwd(), "--target-dir", "-r", help="Target project root (defaults to current directory)."),
    name: str = typer.Option(calculate_nowtime_foldername(), "--name", "-n", help="Name of the workspace to create."),
    #here: bool = typer.Option(False, "--here", "-h", help="The new named workspace directory should be placed immediately in the current working directory, rather than nested within a `/workspaces/` directory. The `--here` flag can only be used with the `--bare` flag."),
    #set_default: bool = typer.Option(True, "--set-default/--no-set-default", help="Write default-workspace.toml"),
    enforce_mulch_folder: bool = typer.Option(False,"--enforce-mulch-folder-only-no-fallback", "-e", help = "This is leveraged in the CLI call by the context menu Mulch command PS1 to ultimately mean 'If you run Mulch and there is no .mulch folder, one will be generated. If there is one, it will use the default therein.' "),
    stealth: bool = typer.Option(False, "--stealth", "-s", help="Put source files in .mulch/src/ instead of root/src/. Workspace still built in root."),
    ):
    """
    Build the workspace_manager.py file in the source code, using the mulch-scaffold.json structure or the fallback structure embedded in WorkspaceFactory.
    Establish a logs folder at root, with the logging.json file.
    """
    
    # The enforce_mulch_folder flag allows the _all_order_of_respect_failed to reach the end of the order_of_respect list, such that a generation of a `.mulch` folder is forceable, without an explicit `mulch folder` call. Otherwise, `mulch` as a single context menu command would use some fallback, rather than forcing a `.mulch` folder to be created, which it should if there is not one.
    # The `mulch` command by itself in the context menu means either 
    if enforce_mulch_folder:
        try:
            scaffold_dict = load_scaffold(
                target_dir=target_dir,
                strict_local_dotmulch=enforce_mulch_folder,
                seed_if_missing=enforce_mulch_folder
            )
        except FileNotFoundError as e:
            typer.secho(str(e), fg=typer.colors.RED)
            raise typer.Exit(code=1)
        order_of_respect_local = ORDER_OF_RESPECT
    else:
        order_of_respect_local = [Path.cwd() / '.mulch']
    
    if _all_order_of_respect_failed(order_of_respect_local):
       make_dot_mulch_folder(target_dir = Path.cwd()) # uses the same logic as the `mulch folder` command. The `mulch file` command must be run manually, for that behavior to be achieved but otherwise the default is the `.mulch` manifestation. This should contain a query tool to build a `mulch-scaffold.toml` file is the user is not comfortable doingediting it themselves in a text editor.

    scaffold_dict = resolve_scaffold(order_of_respect_local, FILENAMES_OF_RESPECT)
    pprint(scaffold_dict)

    lock_data = {
        "scaffold": scaffold_dict,
        "generated_by": f"mulch {MULCH_VERSION}",
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "generated_by": get_username_from_home_directory()
    }
    
    workspace_dir = _determine_workspace_dir(target_dir, name, stealth)
    #manager_status = wf.evaluate_manager_status() # check the lock file in src/-packagename-/mulch.lock, which correlates with the workspacemanager
    wf = WorkspaceFactory(target_dir, workspace_dir, name, lock_data, stealth=stealth)
    wf.build_src_components()
    typer.secho(f"📁 Source code created", fg=typer.colors.BRIGHT_GREEN)

@app.command()
@with_logging
def workspace(
    target_dir: Path = typer.Option(Path.cwd(), "--target-dir", "-r", help="Target project root (defaults to current directory)."),
    name: str = typer.Option(calculate_nowtime_foldername(), "--name", "-n", help="Name of the workspace to create."),
    here: bool = typer.Option(False, "--here", "-h", help="The new named workspace directory should be placed immediately in the current working directory, rather than nested within a `/workspaces/` directory. The `--here` flag can only be used with the `--bare` flag."),
    set_default: bool = typer.Option(True, "--set-default/--no-set-default", help="Write default-workspace.toml"),
    enforce_mulch_folder: bool = typer.Option(False,"--enforce-mulch-folder-only-no-fallback", "-e", help = "This is leveraged in the CLI call by the context menu Mulch command PS1 to ultimately mean 'If you run Mulch and there is no .mulch folder, one will be generated. If there is one, it will use the default therein.' "),
    ):
    """
    Initialize a new workspace folder tree, using the mulch-scaffold.json structure or the fallback structure embedded in WorkspaceFactory.
    """
    
    if here:
        typer.secho(f"`here`: True.",fg=typer.colors.MAGENTA)

    # The enforce_mulch_folder flag allows the _all_order_of_respect_failed to reach the end of the order_of_respect list, such that a generation of a `.mulch` folder is forceable, without an explicit `mulch folder` call. Otherwise, `mulch` as a single context menu command would use some fallback, rather than forcing a `.mulch` folder to be created, which it should if there is not one.
    # The `mulch` command by itself in the context menu means either 
    if enforce_mulch_folder:
        try:
            scaffold_dict = load_scaffold(
                target_dir=target_dir,
                strict_local_dotmulch=enforce_mulch_folder,
                seed_if_missing=enforce_mulch_folder
            )
        except FileNotFoundError as e:
            typer.secho(str(e), fg=typer.colors.RED)
            raise typer.Exit(code=1)
        order_of_respect_local = ORDER_OF_RESPECT
    else:
        order_of_respect_local = [Path.cwd() / '.mulch']
    
    if _all_order_of_respect_failed(order_of_respect_local):
       make_dot_mulch_folder(target_dir = Path.cwd()) # uses the same logic as the `mulch folder` command. The `mulch file` command must be run manually, for that behavior to be achieved but otherwise the default is the `.mulch` manifestation. This should contain a query tool to build a `mulch-scaffold.toml` file is the user is not comfortable doingediting it themselves in a text editor.

    #scaffold_dict = None
    scaffold_dict = resolve_scaffold(order_of_respect_local, FILENAMES_OF_RESPECT)
    pprint(scaffold_dict)


    lock_data = {
        "scaffold": scaffold_dict,
        "generated_by": f"mulch {MULCH_VERSION}",
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "generated_by": get_username_from_home_directory()
    }
    
    workspace_dir = _determine_workspace_dir(target_dir, name, here)
    wf = WorkspaceFactory(target_dir, workspace_dir, name, lock_data, here=here)

    workspace_status = wf.evaluate_workspace_status()
    
    if workspace_status == WorkspaceStatus.MATCHES:
        typer.secho(f"✅ Workspace '{name}' is already set up at {workspace_dir}", fg=typer.colors.GREEN)
        typer.echo("   (Scaffold unchanged. Nothing regenerated.)")
        raise typer.Exit()

    elif workspace_status == WorkspaceStatus.DIFFERS:
        typer.secho(f"⚠️  Workspace '{name}' already exists and scaffold has changed.", fg=typer.colors.YELLOW)
        if not typer.confirm("Overwrite existing workspace?", default=False):
            typer.secho("❌ Aborting.", fg=typer.colors.RED)
            raise typer.Exit()

    elif workspace_status == WorkspaceStatus.EXISTS_NO_LOCK:
        typer.secho(f"⚠️  Workspace exists at {workspace_dir} but no scaffold.lock found.", fg=typer.colors.YELLOW)
        if not typer.confirm("Overwrite existing workspace?", default=False):
            typer.secho("❌ Aborting.", fg=typer.colors.RED)
            raise typer.Exit()
        
    # Proceed to generate
    wf.build_workspace(set_default=set_default)
    typer.secho(f"📁 Workspace created at: {workspace_dir}", fg=typer.colors.BRIGHT_GREEN)

    
#@with_logging(use_portable=True)
@app.command()
def file(
    target_dir: Path = typer.Option(Path.cwd(), "--target-dir", "-t", help="Target project root (defaults to current directory)."),
    filepath: str = typer.Option(None, "--filepath", "-f", help=f"Copy an existing scaffold file to the new local {DEFAULT_SCAFFOLD_FILENAME}"),
    use_embedded: bool = typer.Option(False, "--use-embedded-fallback-structure", "-e", help="Use the embedded fallback scaffold."),
    edit: bool = typer.Option(False, "--edit", "-e", help="Open the scaffold file for editing after it's created.")
    ):
    """
    Drop a scaffold file to disk at the target directory.

    Default is the embedded fallback structure. You can optionally copy from another file.
    Use 'show' to preview options.

    Example (PowerShell):
        mulch show -c
        $scaffold_str = '{"": ["config", "data", ...]}'
        $scaffold_str | Out-File -Encoding utf8 -FilePath mulch-scaffold.json
    """
    scaffold_path = target_dir / DEFAULT_SCAFFOLD_FILENAME

    # Step 1: Load scaffold dictionary
    if use_embedded:
        scaffold_dict = FALLBACK_SCAFFOLD
        typer.secho("📦 Using embedded fallback structure.", fg=typer.colors.YELLOW)
    elif filepath:
        scaffold_path_in = Path(filepath)
        scaffold_dict = load_scaffold_file(scaffold_path_in)
        if scaffold_dict is None:
            typer.secho(f"❌ Failed to load scaffold from: {filepath}", fg=typer.colors.RED)
            raise typer.Abort()
        typer.secho(f"✅ Scaffold loaded from: {filepath}", fg=typer.colors.GREEN)
    else:
        # Add order of respect
        scaffold_dict = resolve_scaffold(ORDER_OF_RESPECT, FILENAMES_OF_RESPECT)
        #scaffold_dict = FALLBACK_SCAFFOLD
        #typer.secho("📦 Resolved the scaffold reference.", fg=typer.colors.YELLOW)

    # Step 2: Confirm overwrite
    if scaffold_path.exists():
        if not typer.confirm(f"⚠️ {scaffold_path} already exists. Overwrite?"):
            raise typer.Abort()

    # Step 3: Write JSON scaffold
    with open(scaffold_path, "w", encoding="utf-8") as f:
        json.dump(scaffold_dict, f, indent=2)
    typer.echo(f"✅ Wrote scaffold to: {scaffold_path}")

    # Step 4: Optional edit
    if edit or typer.confirm("📝 Would you like to open the scaffold file for editing now?"):
        open_editor(scaffold_path)

    typer.secho("✏️  You can now manually edit this file to customize your workspace layout.", fg=typer.colors.CYAN)
    typer.echo("⚙️  Changes to this scaffold file will affect 'mulch init' behavior.")

    # If none worked, fallback to embedded
    #typer.secho("📦 Using embedded fallback scaffold structure.", fg=typer.colors.YELLOW)
    #return WorkspaceFactory.FALLBACK_SCAFFOLD

def load_template_choice_dictionary_from_file():
    """
    Attempts to load a TOML or JSON template choice dictionary from known fallback paths.
    """
    for path in TEMPLATE_CHOICE_DICTIONARY_FILEPATHS:
        if path.is_file():
            data = load_scaffold_file(path)
            if data is not None:
                typer.secho(f"✅ Loaded template choices from: {path}", fg=typer.colors.GREEN)
                return data
            else:
                typer.secho(f"⚠️ Failed to parse {path.name} as TOML or JSON.", fg=typer.colors.YELLOW)
    typer.secho("❌ Failed to load template choice dictionary from any known paths.", fg=typer.colors.RED)
    raise typer.Exit(code=1)

@app.command()
def seed(#def dotmulch( 
    target_dir: Path = typer.Option(Path.cwd(),"--target-dir","-t", help="Target project root (defaults to current directory)."),
    template_choice: bool = typer.Option(None,"--template-choice","-c",help = "Reference a known template for standing up workspace organization."),
    edit: bool = typer.Option(
        False, "--edit", "-e", help="Open the scaffold file for editing after it's created.")
        ):
    """

    Drop a .mulch to disk, at the target directory.
    The default is the next level of fallback in the ORDER_OF_RESPECT list.
    You are able to edit the .mulch/mulch-scaffold file manually.  

    """

    scaffold_dict = resolve_scaffold(ORDER_OF_RESPECT, FILENAMES_OF_RESPECT)
    
    scaffold_path = target_dir / '.mulch' / DEFAULT_SCAFFOLD_FILENAME
    if template_choice:
        typer.secho(f"Choosing scaffold by the template (choose from options)", fg=typer.colors.WHITE)
        template_choice_dict = load_template_choice_dictionary_from_file()
        scaffold_dict = template_choice_dict[template_choice] # template choice must be a number 1-9
    if scaffold_path.exists():
        if not typer.confirm(f"⚠️ {scaffold_path} already exists. Overwrite?"):
            #typer.echo("Aborted: Did not overwrite existing scaffold file.") # this is a redundant message
            raise typer.Abort()
    scaffold_path.parent.mkdir(parents=True, exist_ok=True)
    with open(scaffold_path, "w", encoding="utf-8") as f:
        json.dump(scaffold_dict, f, indent=2)
    
    typer.echo(f"✅ Wrote .mulch to: {scaffold_path}")

    if edit or typer.confirm("📝 Would you like to open the scaffold file for editing now?"):
        open_editor(scaffold_path)

    typer.secho("✏️  You can now manually edit the folder contents to customize your workspace layout and other mulch configuration.",fg=typer.colors.WHITE)
    typer.echo("⚙️  Changes to the scaffold file will directly affect the workspace layout and the generated workspace_manager.py when you run 'mulch init'.")

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
            typer.secho(f"File not found at {filepath}.", fg=typer.colors.RED, bold=True)
            typer.secho(f"Recommendation: use the default file (show -d) or the fallback scaffold (show -e)", fg=typer.colors.YELLOW)
            raise typer.Exit(code=1)
        with open(filepath, "r", encoding="utf-8") as f:
            scaffold = json.load(f)
        logger.debug(f"Structure pulled from the provided filepath: {filepath}")
        typer.secho(f"Loaded scaffold from file: {filepath}", fg=typer.colors.GREEN)
    elif use_default:
        if not default_path.exists():
            typer.secho(f"Default file not found at {default_path}.", fg=typer.colors.RED, bold=True)
            typer.secho(f"Recommendation: use an explicit file (show -p [FILEPATH]) or the fallback scaffold (show -e)", fg=typer.colors.YELLOW)
            raise typer.Exit(code=1)
        with open(default_path, "r", encoding="utf-8") as f:
            scaffold = json.load(f)
        logger.debug(f"Structure pulled from the default filepath: {default_path}")
    elif use_embedded:
        scaffold = FALLBACK_SCAFFOLD
        logger.debug(f"Structure pulled from the FALLBACK_SCAFFOLD embedded in workspace_factory.py.")
        typer.secho("Loaded scaffold from embedded fallback structure.", fg=typer.colors.GREEN)
    else:
        if default_path.exists():
            with open(default_path, "r", encoding="utf-8") as f:
                scaffold = json.load(f)
                logger.debug(f"Structure pulled from the default filepath: {default_path}")
                typer.secho(f"Loaded scaffold from default file: {default_path}", fg=typer.colors.GREEN)
        else:
            scaffold = FALLBACK_SCAFFOLD
            logger.debug(f"Structure pulled from the FALLBACK_SCAFFOLD embedded in workspace_factory.py.")
            typer.secho("Loaded scaffold from embedded fallback structure.", fg=typer.colors.GREEN)
    
    print("\n")
    if collapsed:
        typer.echo(json.dumps(scaffold, separators=(",", ":")))
    else:
        typer.echo(json.dumps(scaffold, indent=2))
    
if __name__ == "__main__":
    app()
