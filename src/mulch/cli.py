# src/mulch/cli.py

import typer
import json
import toml
from pathlib import Path
import logging
import datetime
from importlib.metadata import version, PackageNotFoundError
import subprocess

from mulch.decorators import with_logging
from mulch.workspace_factory import WorkspaceFactory
from mulch.logging_setup import setup_logging, setup_logging_portable
from mulch.helpers import calculate_nowtime_foldername


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

FALLBACK_SCAFFOLD = WorkspaceFactory.FALLBACK_SCAFFOLD
HELP_TEXT = "Mulch CLI for scaffolding Python project workspaces."
DEFAULT_SCAFFOLD_FILENAME = 'mulch-scaffold.json'
LOCK_FILE_NAME = 'mulch.lock'

# look for: '.\mulch-scaffold.toml','.\mulch-scaffold.json': in each of these directories 
order_of_respect = [Path('.\\.mulch\\'),
                    Path('.\\'),
                    Path('C:\\Users\\george.bennett\\.mulch\\'),
                    Path('C:\\Users\\george.bennett\\AppData\\.mulch\\'),
                    Path('C:\\Users\\george.bennett\\pipx\\venvs\\mulch\\.mulch\\'),
                    'FALLBACK_SCAFFOLD']
FILENAMES_OF_RESPECT = ['.\mulch-template.toml.j2','.\mulch-scaffold.toml','.\mulch-scaffold.json']
TEMPLATE_CHOICE_DICTIONARY_FILEPATHS = [order_of_respect / 'mulch-scaffold-template-dictionary.toml']

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

def _should_generate_workspace(workspace_dir: Path, lock_data: dict) -> bool:
    lock_path = workspace_dir / LOCK_FILE_NAME

    if workspace_dir.exists():
        if lock_path.exists():
            with open(lock_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
            existing_scaffold = existing.get("scaffold", {})
            if existing_scaffold == lock_data["scaffold"]:
                typer.secho("✅ Scaffold matches existing scaffold.lock. Skipping workspace generation.", fg=typer.colors.BLUE)
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

def _determine_workspace_dir(target_dir, name, here, bare):
    if not here:
        workspace_dir = target_dir / "workspaces" / name
    elif here and bare:
        workspace_dir = target_dir / name
    elif here and not bare:
        typer.secho(f"The `--here/-h` flag requires that the `--bare/-b` flag is also used.",fg=typer.colors.RED)
        raise typer.Abort()
    return workspace_dir # type: ignore

def _init_workspace(target_dir: Path, workspace_dir: Path, name: str, lock_data: dict, set_default: bool, here: bool, bare: bool) -> WorkspaceFactory:
    """
    Shared internal logic to scaffold workspace directories.
    """
    
    target_dir = target_dir.resolve()
    wf = WorkspaceFactory(base_path=target_dir, workspace_dir = workspace_dir, workspace_name=name, lock_data = lock_data)
    wf.check_and_create_workspace_dirs_from_scaffold(workspace_dir)
    typer.secho(f"Workspace '{name}' initialized at {workspace_dir}",fg=typer.colors.BRIGHT_MAGENTA)

    if set_default and not here and not bare:
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
            typer.confirm(
                f"⚠️ {LOCK_FILE_NAME} already exists at {lock_path}, but the scaffold structure has changed.\n"
                f"Overwriting may cause incompatibility with this workspace.\n"
                f"Continue?",
                abort=True
            )

    with open(lock_path, "w", encoding="utf-8") as f:
        json.dump(lock_data, f, indent=2)
    logger.debug(f"Wrote {LOCK_FILE_NAME} to {lock_path}")

def _render_workspace_manager(target_dir: Path, workspace_dir: Path, lock_data: dict):
    """
    Shared internal logic to render workspace_manager.py.
    """
        
    wf = WorkspaceFactory(base_path=target_dir, workspace_dir= workspace_dir,workspace_name="placeholder_workspace_name", lock_data = lock_data)
    wf.render_workspace_manager()
    return

def _establish_software_elements(target_dir: Path):
    pass

def _all_order_of_respect_failed(order_of_respect):
    failed = True
    for path in order_of_respect:
        if Path(path).exists():
            failed = False
    return failed

def make_dot_mulch_folder(target_dir):
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
    scaffold_filepath: str = typer.Option(None, "--filepath", "-f", help="File holding scaffold structure to determine the folder hierarchy for each workspace."),
    bare: bool = typer.Option(False, "--bare", "-b", help="Don't build source code or logs, just make scaffolded workspace directories!"),
    here: bool = typer.Option(False, "--here", "-h", help="The new named workspace directory should be placed immediately in the current working directory, rather than nested within a `/workspaces/` directory. The `--here` flag can only be used with the `--bare` flag."),
    set_default: bool = typer.Option(True, "--set-default/--no-set-default", help="Write default-workspace.toml"),
    enforce_mulch_folder: bool = typer.Option(False,"--enforce-mulch-folder-only-no-fallback", "-e", help = "This is leveraged in the CLI call by the context menu Mulch command PS1 to ultimately mean 'If you run Mulch and there is no .mulch folder, one will be generated. If there is one, it will use the default therein.' ")

):
    """
    Initialize a new workspace folder tree, using the mulch-scaffold.json structure or the fallback structure embedded in WorkspaceFactory.
    Build the workspace_manager.py file in the source code.
    Establish a logs folder at root, with the logging.json file.
    """

    
    # The enforce_mulch_folder flag allows the _all_order_of_respect_failed to reach the end of the order_of_respect list, such that a generation of a `.mulch` folder is forceable, without an explicit `mulch folder` call. Otherwise, `mulch` as a single context menu command would use some fallback, rather than forcing a `.mulch` folder to be created, which it should if there is not one.
    # The `mulch` command by itself in the context menu means either 
    if enforce_mulch_folder:
        order_of_respect = ['.\.mulch']
    
    if _all_order_of_respect_failed(order_of_respect):
       make_dot_mulch_folder(target_dir = Path.cwd()) # uses the same logic as the `mulch folder` command. The `mulch file` command must be run manually, for that behavior to be achieved but otherwise the default is the `.mulch` manifestation. This should contain a query tool to build a `mulch-scaffold.toml` file is the user is not comfortable doingediting it themselves in a text editor.

    if here:
        typer.secho(f"`here`: `bare` value forced to True.",fg=typer.colors.MAGENTA)
        bare = True
    if bare:
        typer.secho(f"`bare`: Source code and logging control will not generated.",fg=typer.colors.MAGENTA)
    

    scaffold_dict = None

    if scaffold_filepath:
        with open(scaffold_filepath, "r", encoding="utf-8") as f:
            scaffold_dict = json.load(f)
        typer.secho(f"Scaffold loaded from explicitly provided file",fg=typer.colors.WHITE)
        logger.debug(f"Scaffold loaded from explicitly provided file: {scaffold_filepath}")

    else:
        default_scaffold_path = target_dir / DEFAULT_SCAFFOLD_FILENAME
        if default_scaffold_path.is_file():
            with open(default_scaffold_path, "r", encoding="utf-8") as f:
                scaffold_dict = json.load(f)
            typer.secho(f"Scaffold loaded from default file.",fg=typer.colors.WHITE)
            logger.debug(f"Scaffold loaded from default file. {default_scaffold_path}")
        else:
            scaffold_dict = FALLBACK_SCAFFOLD
            typer.secho("Scaffold loaded from embedded fallback structure.",fg=typer.colors.WHITE)
            logging.debug("Scaffold loaded from embedded fallback structure.")

    lock_data = {
        "scaffold": scaffold_dict,
        "generated_by": f"mulch {MULCH_VERSION}",
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    

    workspace_dir = _determine_workspace_dir(target_dir, name, here, bare)
    
    if _should_generate_workspace(workspace_dir, lock_data):
        wf = _init_workspace(target_dir, workspace_dir, name, lock_data, set_default, here, bare)
        _generate_workspace_lockfile(workspace_dir, lock_data)
        if not bare:
            _render_workspace_manager(target_dir, workspace_dir, lock_data)
            _establish_software_elements(target_dir)
            setup_logging()
        wf.seed_scaffolded_workspace_files()
    else:
        typer.echo(f"Workspace '{name}' already exists and is up-to-date with the scaffold.")


@app.command()
#@with_logging(use_portable=True)
def file(
    target_dir: Path = typer.Option(Path.cwd(),"--target-dir","-t", help="Target project root (defaults to current directory)."),
    filepath: str = typer.Option(None,"--filepath","-f",help = f"Copy and existing scaffold file to the new local {DEFAULT_SCAFFOLD_FILENAME}"),
    use_embedded: bool = typer.Option(
        False, "--use-embedded-fallback-structure", "-e", help="Reference the embedded fallback structure."
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
    elif filepath:
        with open(filepath, "r", encoding="utf-8") as f:
            scaffold_dict = json.load(f)

    if scaffold_path.exists():
        if not typer.confirm(f"⚠️ {scaffold_path} already exists. Overwrite?"):
            #typer.echo("Aborted: Did not overwrite existing scaffold file.") # this is a redundant message
            raise typer.Abort()
    with open(scaffold_path, "w", encoding="utf-8") as f:
        json.dump(scaffold_dict, f, indent=2)
    
    typer.echo(f"✅ Wrote scaffold to: {scaffold_path}")
    typer.secho("✏️  You can now manually edit this file to customize your workspace layout.",fg=typer.colors.CYAN)
    typer.echo("⚙️  Changes to this scaffold file will directly affect the workspace layout and the generated workspace_manager.py when you run 'mulch init'.")


def _interpret_scaffold_from_order_of_respect(order_of_respect):
    for fallback in order_of_respect:
        # FILENAMES_OF_RESPECT
        scaffold_path_jinja2 = (Path(fallback) / 'mulch-scaffold.toml.j2') 
        #if scaffold_path_jinja2.exists():
        #    with open(scaffold_path_jinja2, "r", encoding="utf-8") as f:
        #        scaffold_dict = jinja.load(f)
        #    return scaffold_dict
        scaffold_path_toml = (Path(fallback) / 'mulch-scaffold.toml')
        if scaffold_path_toml.exists():
            with open(scaffold_path_toml, "r", encoding="utf-8") as f:
                scaffold_dict = toml.load(f)
            return scaffold_dict
        
        scaffold_path_json = (Path(fallback) / 'mulch-scaffold.json')
        if scaffold_path_json.exists():
            with open(scaffold_path_json, "r", encoding="utf-8") as f:
                scaffold_dict = json.load(f)
            return scaffold_dict
        
        if (fallback is WorkspaceFactory.FALLBACK_SCAFFOLD):
            scaffold_dict = fallback
            return scaffold_dict
        else:
            raise typer.Exit(code=1)
            
def load_template_choice_dictionary_from_file():
    for path in TEMPLATE_CHOICE_DICTIONARY_FILEPATHS:
        try:
            toml.load(path)
        except:
            try:
                json.load(path)
            except:
                raise typer.Exit(code=1)


@app.command()
def folder(
    target_dir: Path = typer.Option(Path.cwd(),"--target-dir","-t", help="Target project root (defaults to current directory)."),
    use_order_of_respect: bool = typer.Option(True,"--use-order-of-respect","-u",help = "This says that the new mulch-scaffold.* file will be generated with the most elevated template that can be found, in various possible directories, sorted by hierarchy of impact on the global and local system. See: the order_of_respect: list, in mulch/cli.py vars"),
    template_choice: bool = typer.Option(None,"--template-choice","-c",help = "Reference a known template for standing up workspace organization.")
    ):
    """

    Drop a .mulch to disk, at the target directory.
    The default is the next level of fallback in the order_of_respect list.
    You are able to edit the .mulch/mulch-scaffold.* file manually.  

        mulch folder --help
    """
    template_choice_dict = load_template_choice_dictionary_from_file()
    
    scaffold_path = target_dir / DEFAULT_SCAFFOLD_FILENAME
    # Find the scaffold_dict that should be written to this new .mulch folder, based on order_of_respect.
    if use_order_of_respect:
        scaffold_dict = _interpret_scaffold_from_order_of_respect()
    elif template_choice:
        scaffold_dict = template_choice_dict[template_choice] # template choice must be a number 1-9
    if scaffold_path.exists():
        if not typer.confirm(f"⚠️ {scaffold_path} already exists. Overwrite?"):
            #typer.echo("Aborted: Did not overwrite existing scaffold file.") # this is a redundant message
            raise typer.Abort()
    with open(scaffold_path, "w", encoding="utf-8") as f:
        json.dump(scaffold_dict, f, indent=2)
    
    typer.echo(f"✅ Wrote .mulch to: {scaffold_path}")
    typer.secho("✏️  You can now manually edit the folder contents to customize your workspace layout and other mulch configuration.",fg=typer.colors.CYAN)
    typer.echo("⚙️  Changes to the scaffold file `.mulch\mulch-scaffold.*` in will directly affect the workspace layout and the generated workspace_manager.py when you run 'mulch init'.")



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
