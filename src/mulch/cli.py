# src/mulch/cli.py

import typer
import toml
from pathlib import Path
import logging
from enum import Enum
import datetime
from importlib.metadata import version, PackageNotFoundError
from pprint import pprint
from rich.table import Table
from rich.console import Console
import sys

from mulch.decorators import with_logging
from mulch.workspace_manager_generator import WorkspaceManagerGenerator
from mulch.workspace_instance_factory import WorkspaceInstanceFactory
from mulch.logging_setup import setup_logging, setup_logging_portable
from mulch.helpers import dedupe_paths, open_editor, calculate_nowtime_foldername, get_local_appdata_path, get_default_untitled_workspace_name_based_on_operating_system, get_global_config_path, index_to_letters, get_username_from_home_directory
from mulch.commands.dotfolder import create_dot_mulch
from mulch.commands.build_dotmulch_standard_contents import build_dotmulch_standard_contents
from mulch.constants import FALLBACK_SCAFFOLD, LOCK_FILE_NAME, DEFAULT_SCAFFOLD_FILENAME
from mulch.workspace_status import WorkspaceStatus
from mulch.scaffold_loader import load_scaffold_file, resolve_scaffold
from mulch.reference_lock_manager import ReferenceLockManager, build_flags_record


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


HELP_TEXT = "Mulch CLI for scaffolding Python project workspaces."
SCAFFOLD_TEMPLATES_FILENAME = 'mulch-scaffold-template-dictionary.toml'

FILENAMES_OF_RESPECT = [
    'mulch.toml'
]

# Paths are checked in order of respect for loading the scaffold template dictionary.
# These are used when running `mulch file`, `mulch show`, or any command needing layout templates.
ORDER_OF_RESPECT = [
    Path('.mulch'), # project local hidden folder
    Path.home() / '.mulch', # user profile hidden folde
    get_local_appdata_path("mulch"), # OS standard config path
    get_global_config_path("mulch") # Roaming AppData on Windows, ~/.config on Linux/macOS
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

#@app.callback(invoke_without_command=True)
@app.callback()
def main(
    version: bool = typer.Option(None, "--version", callback=lambda v: print_version(v), is_eager=True, help="Show the version and exit.")
):
    """
    Mulch CLI for scaffolding Python project workspaces
    """
    
    lock = ReferenceLockManager.load_lock()
    if lock is None:
        print("Warning: No reference.lock found — run src and workspace commands first.")
    else:
        pass
        # validate, warn, etc

def print_version(value: bool):
    if value:
        try:
            typer.secho(f"mulch {MULCH_VERSION}",fg=typer.colors.GREEN, bold=True)
        except PackageNotFoundError:
            typer.echo("Version info not found")
        raise typer.Exit()

def _all_order_of_respect_failed(order_of_respect):
    failed = True
    for path in order_of_respect:
        if Path(path).exists():
            failed = False
    return failed

def make_dot_mulch_folder(target_dir):
    return create_dot_mulch(target_dir, order_of_respect=ORDER_OF_RESPECT)

@app.command()
@with_logging
def src(
    target_dir: Path = typer.Option(Path.cwd(), "--target-dir", "-r", help="Target project root (defaults to current directory)."),
    #enforce_mulch_folder: bool = typer.Option(False,"--enforce-mulch-folder-only-no-fallback", "-e", help = "This is leveraged in the CLI call by the context menu Mulch command PS1 to ultimately mean 'If you run Mulch and there is no .mulch folder, one will be generated. If there is one, it will use the default therein.' "),
    stealth: bool = typer.Option(False, "--stealth", "-s", help="Put source files in .mulch/src/ instead of src/."),
    force: bool = typer.Option(False, "--force", help="Override existing, forced."),
    expliref: bool = typer.Option(None, "--wrkspc-in-root/--wrkspc-in-wrkspc", "-wr/-ww", help="Allows you to run src command without first running the workspace command and without a prompt for more input. ww correlates here flag, wr correlates with late thereof."),
    name: str = typer.Option(None, "--name", "-n", help="Name of the src dir to create, in src/.")
    ):
    """
    Build the workspace_manager.py file in the source code, using the mulch.toml structure or the fallback structure embedded in WorkspaceManagerGenerator.
    Establish a logs folder at root, with the logging.json file.
    """
    command_line = ""#.join(sys.argv) # broken currently
    command_line = "null"
    typer.echo(f"command_line = {command_line}")
    flags = build_flags_record(expliref=expliref,force=force,stealth=stealth,name=name)
    if name is None:
        project_name = target_dir.name
    else: 
        project_name = name
    
    '''
    ## A Rule: Run `mulch workspace` at least once before running `mulch src`
    (particularly if you want to run `mulch workspace --here`)
    - For `mulch src` to make the proper references, if you plan to use `--here` flag, you must run `mulch workspace --here` at least once first, to contribute some truth to the `.mulch/reference.lock` file.
    - If you run `mulch src` without first running `mulch workspace`, the workspace_manager.py references will include to the standard /workspaces/ reference, as if the `--here` flag was not used.
    '''
    # Set and infer the embedded reference location for workspace_manager, in case you want to successfully run `mulch src` before 
    if expliref is not None: # Note that this is the src command, not the workspace command.
        ReferenceLockManager.update_lock_workspace(pathstr="null", command_line = command_line, flags=flags) # "null" as a string is acceptable for pathstr, because if no workspace registered yet, expliref provides a basis for the workspace_manager.py references to be generated.

    order_of_respect_local = ORDER_OF_RESPECT
    if _all_order_of_respect_failed(order_of_respect_local):
       make_dot_mulch_folder(target_dir = Path.cwd()) # uses the same logic as the `mulch workspace` command. The `mulch file` command must be run manually, for that behavior to be achieved but otherwise the default is the `.mulch` manifestation. This should contain a query tool to build a `mulch.toml` file is the user is not comfortable doingediting it themselves in a text editor.

    scaffold_data = resolve_scaffold(order_of_respect_local, FILENAMES_OF_RESPECT)
    
    # Create lock data
    lock_data = {   
        "scaffold": scaffold_data,
        "generated_by": f"mulch {MULCH_VERSION}",
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "generated_by": get_username_from_home_directory()
    }
    
    #manager_status = wf.evaluate_manager_status() # check the lock file in src/-packagename-/mulch.lock, which correlates with the workspacemanager
    
    #--- TO DO
    # - generate default name to this level, based on the project folder (CWD) name, and allow for override if --name flag is provided
    # some of the language here is confusing, because the /src/ folder will be built in the cwd is the stealth  
    mgf = WorkspaceManagerGenerator(base_path = target_dir, project_name = project_name, lock_data = lock_data, stealth=stealth, force=force)
    was_source_generated = mgf.build_src_components()
    if was_source_generated:
        typer.secho(f"📁 Source code created", fg=typer.colors.BRIGHT_GREEN)    
        # create reference lock file contents for src
        flags = build_flags_record(expliref=expliref,force=force,stealth=stealth)
        ReferenceLockManager.update_lock_src(pathstr=str(mgf.src_path), command_line = command_line ,flags=flags) # convert Path to str for serialization, at the point of input for clarity. "null" is acceptable as a string.

class NamingPattern(str,Enum):
    date = "date"
    new = "new"

def get_folder_name(pattern: NamingPattern = 'date', base_name: str = "New workspace", workspaces_dir: Path = Path.cwd() / "workspaces") -> str:
    '''
    Dynamically generate a workspace folder name based on the chosen pattern.
    Implementation, if the '--name' flag is not used with `mulch workspace`:
     - Default to {date}, and then {date}b, {date}c, {date}d
     - If the '--pattern new' is used when calling `mulch workspace`, the generated name will be 'New workspace', then 'New workspace (2)', etc, if Windows.   
     - 'mulch workspace --pattern new --here' will be used as the default register context menu command for 'mulch workspace', using the mulch-workspace.reg file. 
    '''
    
    if pattern == NamingPattern.date:
        suffix_index = 0
        while True:
            if suffix_index == 0:
                folder_name = calculate_nowtime_foldername()
            else:
                # Skip 'a', start from 'b'
                suffix = index_to_letters(suffix_index + 1)
                folder_name = f"{calculate_nowtime_foldername()}{suffix}"
            if not (workspaces_dir / folder_name).exists(): # 
                return folder_name
            suffix_index += 1
    elif pattern == NamingPattern.new:
        # check for existing workspace folders to append (n) if necessary, like "New workspace (2)", to mimmick windows "New folder (2)" behavior.
        return get_default_untitled_workspace_name_based_on_operating_system(workspaces_dir)
        

@app.command()
@with_logging
def workspace(
    target_dir: Path = typer.Option(Path.cwd(), "--target-dir", "-r", help="Target project root (defaults to current directory)."),
    pattern: NamingPattern = typer.Option(None, "--pattern", "-p",  help = "Choose naming pattern: 'date' for YYY_MMMMM_DD, or 'new' for os-specific pattern like 'New workspace (n)'"),
    name: str = typer.Option(None, "--name", "-n", help="Name of the workspace to create."),
    here: bool = typer.Option(False, "--here", "-h", help="The new named workspace directory should be placed immediately in the current working directory, rather than nested within a `/workspaces/` directory."),
    set_default: bool = typer.Option(True, "--set-default/--no-set-default", help="Write default-workspace.toml"),
    #enforce_mulch_folder: bool = typer.Option(False,"--enforce-mulch-folder-only-no-fallback", "-e", help = "This is leveraged in the CLI call by the context menu Mulch command PS1 to ultimately mean 'If you run Mulch and there is no .mulch folder, one will be generated. If there is one, it will use the default therein.' "),
    ):
    """
    Initialize a new workspace folder, using the mulch.toml structure or the fallback structure embedded in WorkspaceManagerGenerator.
    """
    command_line = ""#.join(sys.argv) # broken currently
    command_line = "null"
    #typer.echo(f"command_line = {command_line}")
    # Provide instant feedback on the --here setting, if used.
    if here:
        logger.debug(f"`here`: True")
    
    # First determine workspaces directory
    workspaces_dir = WorkspaceInstanceFactory.determine_workspaces_dir(
        target_dir=target_dir,
        here=here
    )
    # Second determine the flags used from the command line and record them, before they are changed in steps Three and Four immediately below.
    flags = build_flags_record(here=here,name=name,pattern=pattern)
    # Third, use the default pattern, if the pattern flag was not used.
    if pattern is None:
        pattern = NamingPattern.date # only necessary if name is None
    # Fourth, assign the patterned name, if the name flag was not used to supply the name explicitly.
    if name is None:
        name=get_folder_name(pattern = pattern, workspaces_dir=workspaces_dir)
    
    order_of_respect_local = ORDER_OF_RESPECT
    if _all_order_of_respect_failed(order_of_respect_local):
       make_dot_mulch_folder(target_dir = Path.cwd()) # uses the same logic as the `mulch workspace` command. The `mulch file` command must be run manually, for that behavior to be achieved but otherwise the default is the `.mulch` manifestation. This should contain a query tool to build a `mulch.toml` file is the user is not comfortable doingediting it themselves in a text editor.

    scaffold_data = resolve_scaffold(order_of_respect_local, FILENAMES_OF_RESPECT)
    
    # Create lock data
    lock_data = {
        "scaffold": scaffold_data,
        "generated_by": f"mulch {MULCH_VERSION}",
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "generated_by": get_username_from_home_directory()
    }
    
    logger.debug(f"workspace_dirs = {workspaces_dir}")
    wif = WorkspaceInstanceFactory(target_dir, workspaces_dir, name, lock_data, here=here)
    
    workspace_status = wif.evaluate_workspace_status()
    
    if workspace_status == WorkspaceStatus.MATCHES:
        typer.secho(f"✅ Workspace '{name}' is already set up in {workspaces_dir}", fg=typer.colors.GREEN)
        typer.echo("   (Scaffold unchanged. Nothing regenerated.)")
        raise typer.Exit()

    elif workspace_status == WorkspaceStatus.DIFFERS:
        typer.secho(f"⚠️  Workspace '{name}' already exists and scaffold has changed.", fg=typer.colors.YELLOW)
        if not typer.confirm("Overwrite existing workspace?", default=False):
            typer.secho("❌ Aborting.", fg=typer.colors.RED)
            raise typer.Exit()

    elif workspace_status == WorkspaceStatus.EXISTS_NO_LOCK:
        typer.secho(f"⚠️  Workspace exists at {workspaces_dir / name} but no scaffold.lock found.", fg=typer.colors.YELLOW)
        if not typer.confirm("Overwrite existing workspace?", default=False):
            typer.secho("❌ Aborting.", fg=typer.colors.RED)
            raise typer.Exit()
        
    # Proceed to generate
    wif.create_workspace(set_default=set_default)

    # create reference lock file contents for workspace 
    ReferenceLockManager.update_lock_workspace(pathstr=str(workspaces_dir / name), command_line = command_line, flags=flags)
    
@app.command()
def context():
    """
    Install the right-click `mulch workspace` context menu registry item.
    """
    from mulch.scripts.install import install_context
    install_context.setup()
    
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
def seed(
    target_dir: Path = typer.Option(Path.cwd(), "--target-dir", "-t", help="Target project root (defaults to current directory)."),
    index: int = typer.Option(None, "--index", "-i", help="Index from 'mulch order' to choose scaffold source."),
    template_choice: bool = typer.Option(None, "--template-choice", "-c", help="Reference a known template for workspace organization."),
    edit: bool = typer.Option(False, "--edit", "-e", help="Open scaffold file for editing after creation."),
):
    """
    Drop a .mulch folder to disk at the target directory.
    The scaffold source can be selected by index (from 'mulch order') or by template choice.
    You can edit the .mulch/mulch.toml file manually. Coming soon: interactive prompt file filler.
    """
    sources = get_ordered_sources()

    # Determine scaffold_dict depending on index or template_choice
    if index is not None:
        if index < 1 or index > len(sources):
            raise typer.Exit(f"Invalid index {index}. Run 'mulch order' to see valid indices.")
        selected_source = sources[index - 1]

        if selected_source == "FALLBACK_SCAFFOLD":
            typer.echo(f"Using scaffold from embedded fallback (order index {index}).")
            scaffold_dict = FALLBACK_SCAFFOLD
        else:
            # Compose path to mulch.toml and load if exists
            scaffold_path = (target_dir / selected_source) if not Path(selected_source).is_absolute() else Path(selected_source)
            scaffold_path = (scaffold_path / "mulch.toml").resolve()

            if scaffold_path.exists():
                typer.echo(f"Using scaffold from file: {scaffold_path} (order index {index})")
                with open(scaffold_path, "r", encoding="utf-8") as f:
                    scaffold_dict = toml.load(f)
            else:
                raise typer.Exit(f"No scaffold file found at {scaffold_path}")

    elif template_choice:
        typer.secho(f"Choosing scaffold by template (choose from options)", fg=typer.colors.WHITE)
        template_choice_dict = load_template_choice_dictionary_from_file()
        scaffold_dict = template_choice_dict[template_choice]  # Make sure template_choice is a valid key
        path = "DEVELOPMENT: template_choice is not implemented yet, but it will be a number 1-9."
        typer.echo(f"Using template from file: {path}")

    else:
        # Neither index nor template choice: pick first available scaffold from sources
        scaffold_dict = None
        for idx, source in enumerate(sources, start=1):
            if source == "FALLBACK_SCAFFOLD":
                typer.echo(f"Using scaffold from embedded fallback (order index {idx}).")
                scaffold_dict = FALLBACK_SCAFFOLD
                break
            path = (target_dir / source) if not Path(source).is_absolute() else Path(source)
            path = (path / "mulch.toml").resolve()
            if path.exists():
                typer.echo(f"Using scaffold from file: {path} (order index {idx})")
                with open(path, "r", encoding="utf-8") as f:
                    scaffold_dict = toml.load(f)
                break

        if scaffold_dict is None:
            raise typer.Exit("No available scaffold found in any source.")

    # Write scaffold to target_dir/.mulch/mulch.toml
    output_path = target_dir / ".mulch" / DEFAULT_SCAFFOLD_FILENAME
    if output_path.exists() and not typer.confirm(f"⚠️ {output_path} already exists. Overwrite?"):
        raise typer.Abort()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        toml.dump(scaffold_dict, f)

    typer.echo(f"✅ Wrote .mulch to: {output_path}")

    if edit or typer.confirm("📝 Would you like to open the scaffold file for editing now?"):
        open_editor(output_path)

    typer.secho(
        "✏️  You can now manually edit the folder contents to customize your workspace layout and other mulch configuration.",
        fg=typer.colors.WHITE,
    )
    typer.echo(
        "⚙️  Changes to the scaffold file will directly affect the workspace layout and the generated workspace_manager.py when you run 'mulch src'."
    )

    build_dotmulch_standard_contents(target_dir=target_dir)

#@with_logging(use_portable=True)
@app.command()
def order(target_dir: Path = typer.Option(Path.cwd(), "--target-dir", "-t")):
    """
    Show the ordered list of mulch scaffold search paths, and also the FALLBACK_SCAFFOLD variable, and indicate which exist.
    """
    console = Console()
    sources = get_ordered_sources()

    typer.echo(f"Mulch Scaffold Order of Respect:")
    for idx, source in enumerate(sources, start=1):
        if source == "FALLBACK_SCAFFOLD":
            display_path = "FALLBACK_SCAFFOLD"
            exists = True  # Always exists because embedded
            typer.echo(f"  {idx}: FALLBACK_SCAFFOLD  ({'exists' if exists else 'does not exist'})")

        else:
            base_path = (target_dir / source) if not Path(source).is_absolute() else Path(source)
            resolved_path = (base_path / "mulch.toml").resolve()
            display_path = str(resolved_path)
            exists = resolved_path.exists()
            typer.echo(f"  {idx}: {display_path} ({'exists' if exists else 'does not exist'})")

        
    table = Table(title="Mulch Scaffold Order of Respect")
    table.add_column("Index", justify="right", style="cyan", no_wrap=True)
    table.add_column("Path", style="magenta")
    table.add_column("Exists?", justify="center", style="green")

    for idx, source in enumerate(sources, start=1):
        if source == "FALLBACK_SCAFFOLD":
            display_path = "FALLBACK_SCAFFOLD"
            exists = True  # Always exists because embedded
        else:
            base_path = (target_dir / source) if not Path(source).is_absolute() else Path(source)
            resolved_path = (base_path / "mulch.toml").resolve()
            display_path = str(resolved_path)
            exists = resolved_path.exists()

        table.add_row(str(idx), display_path, "✅" if exists else "❌")

    console.print(table)

def get_ordered_sources():
    return list(dedupe_paths(ORDER_OF_RESPECT)) + ["FALLBACK_SCAFFOLD"]

@app.command()
def show(index: int = typer.Argument(None, help="Index from 'mulch order' to display"),
         target_dir: Path = typer.Option(Path.cwd(), "--target-dir", "-t")):
    """
    Show the scaffold from the first available source in the order of respect,
    or from the specific index if provided.
    """
    sources = get_ordered_sources()

    if index is not None:
        if index < 1 or index > len(sources):
            raise typer.Exit(f"Invalid index {index}. Run 'mulch order' to see valid indices.")

        selected = sources[index - 1]

        if selected == "FALLBACK_SCAFFOLD":
            scaffold = FALLBACK_SCAFFOLD  # your embedded dict
            print("Loaded scaffold from embedded fallback structure.")
            print(toml.dumps(scaffold))
            return

        path = (target_dir / selected) if not Path(selected).is_absolute() else Path(selected)
        path = (path / "mulch.toml").resolve()

        if path.exists():
            typer.echo(f"Loaded scaffold from: {path}")
            with open(path, "r", encoding="utf-8") as f:
                scaffold = toml.load(f)
            print(toml.dumps(scaffold))
            return
        else:
            raise typer.Exit(f"No scaffold file found at: {path}")

    else:
        # No index given: check all sources in order until one loads
        for source in sources:
            if source == "FALLBACK_SCAFFOLD":
                scaffold = FALLBACK_SCAFFOLD
                print("Loaded scaffold from embedded fallback structure.")
                print(toml.dumps(scaffold))
                return

            path = (target_dir / source) if not Path(source).is_absolute() else Path(source)
            path = (path / "mulch.toml").resolve()

            if path.exists():
                typer.echo(f"Loaded scaffold from: {path}")
                with open(path, "r", encoding="utf-8") as f:
                    scaffold = toml.load(f)
                print(toml.dumps(scaffold))
                return

        raise typer.Exit("No scaffold found in any source.")

if __name__ == "__main__":
    app()
