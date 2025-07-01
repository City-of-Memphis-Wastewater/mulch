# wsmx — Workspace Manager CLI

`wsmx` is a lightweight, project-agnostic CLI tool to scaffold and manage workspace directories
for any Python project. It bootstraps a standardized workspace folder structure and configuration
files inside your project directory.

---

## Features

- Initialize workspaces with a consistent scaffold defined by `scaffold.json`
- Create a `default-workspace.toml` to track the active workspace
- Works standalone and project-agnostic; no assumptions about your repo layout
- Easily installable and runnable via `pipx`

---

# Installation

## pipx
```bash
pipx install wsmx
```

## git clone

```bash
git clone https://github.com/yourusername/wsmx.git
cd wsmx
poetry install
poetry build
pipx install dist/wsmx-0.1.0-py3-none-any.whl
```


# Usage

```bash
# Initialize workspace named 'default' in the current directory
wsmx

# Initialize workspace named 'workspace1' in ./myproject
wsmx ./myproject --name workspace1

# Initialize workspace named 'workspace1' in the current directory
wsmx --name workspace1

# Skip creating default-workspace.toml
wsmx ./myproject --name workspace1 --no-set-default
```

# Setup

## From the root of your wsmx repo
poetry build

## Install it with pipx
pipx install dist/wsmx-0.1.0-py3-none-any.whl

## Now you can run:
wsmx --help
wsmx init ./target-software

