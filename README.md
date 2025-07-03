# mulch — Workspace Factory CLI

`mulch` is a lightweight, project-agnostic CLI tool to scaffold and generate workspace directories
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
# Initialize workspace named 'default' in the current directory
mulch init

# Initialize workspace named 'workspace1' in ./myproject
mulch init ./myproject --name workspace1

# Initialize workspace named 'workspace1' in the current directory
mulch init --name workspace1

# Skip creating default-workspace.toml
mulch init ./myproject --name workspace1 --no-set-default
```

