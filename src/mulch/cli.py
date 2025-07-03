# src/mulch/cli.py

import typer
from pathlib import Path
from mulch.workspace_factory import WorkspaceFactory

HELP_TEXT = "Mulch CLI for scaffolding Python project workspaces."

app = typer.Typer(help=HELP_TEXT, no_args_is_help=True)


@app.callback()
def main():
    """
    {{ HELP_TEXT }}
    """
    pass


def _init_workspace(target_dir: Path, name: str, set_default: bool) -> WorkspaceFactory:
    """
    Shared internal logic to scaffold workspace directories.
    """
    target_dir = target_dir.resolve()
    wf = WorkspaceFactory(base_path=target_dir, workspace_name=name)
    wf.check_and_create_dirs_from_scaffold()

    if set_default:
        wf.create_default_workspace_toml(target_dir / "workspaces", name)

    return wf


def _render_workspace_manager(target_dir: Path, project_name: str):
    """
    Shared internal logic to render workspace_manager.py.
    """
    wf = WorkspaceFactory(base_path=target_dir, workspace_name="placeholder")
    wf.render_workspace_manager(project_name=project_name)
    return


@app.command()
def init(
    target_dir: Path = typer.Argument(Path.cwd(), help="Target project root (defaults to current directory)."),
    name: str = typer.Option("default", "--name", "-n", help="Name of the workspace to create."),
    set_default: bool = typer.Option(True, "--set-default/--no-set-default", help="Write default-workspace.toml")
):
    """
    Initialize a new workspace folder tree using scaffold.json or fallback.
    """
    wf = _init_workspace(target_dir, name, set_default)
    typer.echo(f"Workspace '{name}' initialized at {wf.workspace_dir}")


@app.command("render")
def render(
    target_dir: Path = typer.Argument(Path.cwd(), help="Target project root (where scaffold.json lives)."),
    project_name: str = typer.Option(..., "--project", "-p", help="Project name used for src/<project>/workspace_manager.py")
):
    """
    Render workspace_manager.py using scaffold.json and a Jinja2 template.
    """
    _render_workspace_manager(target_dir, project_name)
    typer.echo(f"workspace_manager.py created in src/{project_name}/")


if __name__ == "__main__":
    app()
