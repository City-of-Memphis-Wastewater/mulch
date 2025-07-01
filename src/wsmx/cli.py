# src/wsmx/cli.py

import typer
from pathlib import Path
from wsmx.workspace_manager import WorkspaceManager

app = typer.Typer(help="Workspace Manager CLI for scaffolding project workspaces.")

@app.command()
def init(
    target_dir: Path = typer.Argument(Path.cwd(), help="Target project root. Defaults to current directory."), # assume you are in pacakge root unless told otherwise
    name: str = typer.Option("default", "--name", "-n", help="Name of the workspace to create."),
    set_default: bool = typer.Option(True, "--set-default/--no-set-default", help="Write default-workspace.toml")
):
    """
    Initialize a new workspace inside the given target directory.
    """
    target_dir = target_dir.resolve()
    wm = WorkspaceManager(base_path=target_dir, workspace_name=name)
    wm.check_and_create_dirs_from_scaffold()

    if set_default:
        #WorkspaceManager.create_default_workspace_toml(wm.base_path / "workspaces", name)
        wm.create_default_workspace_toml(target_dir / "workspaces", name)

    typer.echo(f"Workspace '{name}' initialized at {wm.workspace_dir}")


if __name__ == "__main__":
    app()
