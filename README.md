# mulch — Workspace Factory CLI

`mulch` is a lightweight, project-agnostic CLI tool to scaffold and generate workspace directories
for intentional, usable Python projects. It bootstraps a standardized workspace folder structure, an introspective templated `WorkspaceManager`, and other key files inside both your source directory and your workspaces directory.

Set up new projects easily with workspace scaffolding and source-code templating. 

Key feature: Benefit from introspective directory getters and file getters in the `WorkspaceManager` class, dictated by `mulch-scaffold.json` and protected by `mulch.lock`.

Set up new projects easily with workspace scaffolding and source-code templating. 

Key feature: Benefit from introspective directory getters and file getters in the `WorkspaceManager` class, dictated by `mulch-scaffold.json` and protected by `mulch.lock`.

---

## Features

- Initialize workspaces with a consistent scaffold defined by `mulch-scaffold.json`
- Create a `default-workspace.toml` to track the active workspace
- Easily installable and runnable via `pipx`
- Uses a Pythonic `/package-root/src/pacakge-name/` paradigm
- Enforces a separation of source code and workspace files, with workspace files organized into  `/package-root/workspaces/your-special-workspace/` structure.

---

# Installation

## pipx (recommended)
```bash
pipx install mulch
```
Install Mulch as a right-click item in the context menu:

- [Windows Context Menu Registry](https://gist.github.com/KyleMit/978086ae267ff5be17811e99c9607986)
- [Thunar Custom Actions on Linux](https://docs.xfce.org/xfce/thunar/custom-actions)

## git clone

```bash
git clone https://github.com/city-of-memphis/mulch.git
cd mulch
poetry install
poetry build
pipx install dist/mulch-*-py3-none-any.whl
```


# Usage

```bash
# Generated a fresh mulch-scaffold.json file, to edit before running 'mulch init'.
mulch file

# Initialize workspace named 'default' in the current directory
mulch init

# Initialize workspace named 'workspace1' in ./myproject
mulch init ./myproject --name workspace1

# Initialize workspace named 'workspace1' in the current directory
mulch init --name workspace1

# Skip creating default-workspace.toml
mulch init ./myproject --name workspace1 --no-set-default
```

