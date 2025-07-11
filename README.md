# mulch — Workspace Factory CLI

`mulch` is a lightweight CLI and context menu tool, with multiple directory scaffolding use cases. Developers will enjoy quickly standing up Python projects, and end users will enjoy right clicking in the file browser to set up file organization the same way every time, customizable to each directory.
 

---

## Features

Key feature: Benefit from introspective directory getters and file getters in the `WorkspaceManager` class, dictated by `mulch-scaffold.json` and protected by `manager.lock`.

Key feature: The hidden `.mulch` folder can be leveraged for configuration as well as in `--stealth` mode, so that shared directories can be crisp while given you space to write analysis scripts.

More:
- Easily installable and runnable via `pipx`
- Enforces a separation of source code and workspace files.

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
The git source code includes `.reg` files which can be leveraged to register right-click commands with your context menu, to enjoy the full power of `mulch` in your file browser as a user-facing power tool.

# Usage

```bash
# Set up a new directory, where you anticipate to organizing multiple projects
mkdir equipment-monitoring 
cd equipment-monitoring

# Generated a fresh .mulch\mulch-scaffold.json file, and edit the directory scaffold before running 'mulch init'.
mulch seed --edit

# Stealth mode, best for shared directories
mulch init --name bioreactor-1-team-analysis --stealth 

# Stanadard mode, best for Python developers
mulch init --name API01toAPI05  

```

## Folder Stucture Options, using `mulch init`

| Flag        | Workspace Location   | Source Location      | Goal                        |
| ----------- | -------------------- | -------------------- | --------------------------- |
| *(none)*    | `workspaces/<name>/` | `src/<proj>/`        | Normal development use      |
| `--here`    | `./<name>/`          | *(none)*             | Clean, user-facing          |
| `--bare`    | `workspaces/<name>/` | *(none)*             | New workspace, no src impact|
| `--stealth` | `./<name>/`          | `.mulch/src/<proj>/` | Play nice with shared dirs  |

I am really excited about `mulch init --stealth` for mixed use directories. Business and engineering users can organize projects in a shared drive like SharePoint, while a dev can run custom analysis scripts catered to each type of project. 

