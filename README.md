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

## pipx
```bash
pipx install mulch
```

## git clone

```bash
git clone https://github.com/yourusername/mulch.git
cd mulch
poetry install
poetry build
pipx install dist/mulch-0.1.0-py3-none-any.whl
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

# Setup

## From the root of your mulch repo
poetry build

## Install it with pipx
pipx install dist/mulch-0.1.0-py3-none-any.whl

## Now you can run:
mulch --help
mulch init ./target-software

