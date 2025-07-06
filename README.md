# mulch — Workspace Factory CLI

`mulch` is a lightweight, project-agnostic CLI tool to scaffold and generate workspace directories
for any Python project. It bootstraps a standardized workspace folder structure and configuration
files inside your project directory.

Set up new projects easily with workspace scaffolding and source-code templating. Key feature: Benefit from introspective directory geters and file getters in the workspace_manager.py file in src, dictated by mulch-scaffold.json and protected by mulch.lock.
---

## Features

- Initialize workspaces with a consistent scaffold defined by `mulch-scaffold.json`
- Create a `default-workspace.toml` to track the active workspace
- Works standalone and project-agnostic; no assumptions about your repo layout
- Easily installable and runnable via `pipx`

---

# Installation

## pipx (recommended)
```bash
pipx install mulch
```

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

