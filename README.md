# mulch — Workspace Factory CLI

`mulch` is a lightweight CLI and right-click context menu tool. Use `mulch` to empower your file system. There with multiple use cases for enhanced directory scaffolding, both as an individual and in a shared drive with a team. Developers will enjoy quickly standing up Python projects, and end-users will enjoy right-clicking in the file browser to set up file organization the same way every time, customizable to each directory.
 

---

## Features

- Benefit from introspective directory getters and file getters in the `WorkspaceManager` class, dictated by `mulch-scaffold.json` and protected by `manager.lock`.
- The hidden `.mulch` folder is leveraged for configuration.
- In `--stealth` mode, code can be stashed in `.mulch`, so that workplace directories shared with non-technical co-workers can be crisp while providing space to write localized analysis scripts.
- Easily installable and runnable via `pipx`
- Enforces a separation of source code and workspace files.
- The `--here` flag enables basic scaffolding for directory-only generation, no code included.
- The default workspace folder name is the date, if the `--name` flag is not provided.
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

# Stealth mode, best for shared directories (`--stealth`)
mulch init --stealth
mulch workspace --name bioreactor-1-team-analysis --here 

# Standard mode, best for Python developers
mulch init 
mulch workspace --name API01toAPI05  

# User mode, for everyone (`--here`)
mulch workspace --name SummerPhotos2025 --here 

```

## Folder Stucture Options, using `mulch init`

| Flag        | Workspace Location   | Source Location      | Goal                        |
| ----------- | -------------------- | -------------------- | --------------------------- |
| *(none)*    | `workspaces/<name>/` | `src/<proj>/`        | Normal development use      |
| `--here`    | `./<name>/`          | *(none)*             | Clean, user-facing          |
| `--stealth` | `./<name>/`          | `.mulch/src/<proj>/` | Play nice with shared dirs  |

I am really excited about `mulch init --stealth` for mixed use directories. Business and engineering users can organize projects in a shared drive like SharePoint, while a dev can run custom analysis scripts catered to each type of project. 

