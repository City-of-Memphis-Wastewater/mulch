# mulch — Workspace Factory CLI

`mulch` is a lightweight CLI bootstrapper and right-click context menu tool. Use `mulch` to empower your file system. There with multiple use cases for enhanced directory scaffolding, both as an individual and in a shared drive with a team. Developers will enjoy quickly standing up Python projects, and end-users will enjoy right-clicking in the file browser to set up file organization the same way every time, customizable to each directory.

---

## Features

- Benefit from introspective directory getters and file getters in the `WorkspaceManager` class, dictated by `mulch.toml` and protected by `manager.lock`.
- The hidden `.mulch` folder is leveraged for configuration.
- In `--stealth` mode, code can be stashed in `.mulch`, so that workplace directories shared with non-technical co-workers can be crisp while providing space to write localized analysis scripts.
- Easily installable and runnable via `pipx`
- Enforces a separation of source code and workspace files.
- The `--here` flag enables basic scaffolding for directory-only generation, no code included.
- The default workspace folder name is the date, if the `--name` flag is not provided.
- The `mulch-context` CLI command is registered with the system, as per tool.poetry.scripts, mulch-context = "mulch.scripts.install.install_context:app"

---

# Installation

## pipx (recommended)
```bash
pipx install mulch
mulch-context # or `mulch context`
```

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

# Generated a fresh .mulch\mulch.toml file, and edit the directory scaffold before running 'mulch src'.
mulch seed --edit

# Stealth mode, best for shared directories (`--stealth`)
mulch src --stealth
mulch workspace --name bioreactor-1-team-analysis --here 

# Standard mode, best for Python developers
mulch src 
mulch workspace --name API01toAPI05  

# User mode, for everyone (`--here`)
mulch workspace --name SummerPhotos2025 --here 

# Mimick new folder default naming convention, to invite the user to edit the workspace directory name manually
mulch workspace --pattern new --here # This is the installed context menu behavior, via `mulch-context`

# Use a date as a default new workspace naming convention, for low-friction useful naming. This matches my Obsidian templated date convention. 
# This is the default if the `--pattern` flag is not used explicitly and if an explicit name is not provided with the `--name` flag.
mulch workspace --pattern date --here 
mulch workspace --here # This does the same thing, as of 0.2.19.


```

## Folder Stucture Options, using `mulch src`

| Flag        | Workspace Location   | Source Location      | Goal                        |
| ----------- | -------------------- | -------------------- | --------------------------- |
| *(none)*    | `workspaces/<name>/` | `src/<proj>/`        | Normal development use      |
| `--here`    | `./<name>/`          | *(none)*             | Clean, user-facing          |
| `--stealth` | `./<name>/`          | `.mulch/src/<proj>/` | Play nice with shared dirs  |

I am really excited about `mulch src --stealth` for mixed use directories. Business and engineering users can organize projects in a shared drive like SharePoint, while a dev can run custom analysis scripts catered to each type of project. 

---

## `mulch context` versus `mulch-context`
These do the same thing. 
`mulch-context` is an independant CLI tool to register `mulch workspace` behavior to the context menu.
`mulch context` is a command in the `mulch` CLI, which also calls the `app()` function in `install_context.py`.

---

## Notice: Deprecation of `mulch workspace --stealth`

The `--stealth` flag for the `mulch workspace` command will be **deprecated in an upcoming release**.

### Background and Use Case

The `--stealth` option was originally introduced to allow creating an src directory inside the hidden `.mulch` folder. When `mulch init` split into `mulch src` and `mulch workspace`, the `--stealth` flag was maintained for each. The loose theory was that a stealth option for `workspace` might be useful in supporting workflows where non-technical users focus on visible workspaces while developers maintain custom local software with multiple configurations in hidden workspace folders.

This use case is valid and important for scenarios involving mixed user environments and evolving projects with increasing complexity. However, managing stealth workspaces via this flag can be unintuitive and may cause confusion about the current working directory context.

### Recommended Alternative

To maintain clean and organized hidden workspace directories, if you must have them, we recommend *identifying the target_dir to the `.mulch` folder* by running:

```bash
mulch workspace --target-dir .\.mulch [options]
```

This approach clearly scopes the workspace creation inside the hidden folder without relying on the deprecated `--stealth` flag.

You can choose only one set of workspace references. You can run `mulch src --force` and it will break the references to the public workspace set and build them for the private set. 

---

## A Rule: Run `mulch workspace` at least once before running `mulch src`, particularly if you want to run `mulch workspace --here`
- For `mulch src` to make the proper references, if you plan to use `--here` flag, you must run `mulch workspace --here` at least once first, to contribute some truth to the `.mulch/reference.lock` file.
- If you run `mulch src` without first running `mulch workspace`, the workspace_manager.py references will include to the standard /workspaces/ reference, as if the `--here` flag was not used.
- If you end up running `mulch workspace` without the `--here` flag, I don't think you'll have any trouble.
- The `reference.lock` should enforce consistency, not allowing you to mix `--here` workspaces with lackthereof workspaces in the same project. 
  - This has the added benfit of adjusting the behavior of the context menu `mulch workspace`, which is assumed to be `mulch workspace --here --pattern new`
  - With enforcement from the `reference.lock` file, the `--here` flag can be ignored, if it was initally not used. Is this what we want?  
  - No warning will appear for the context menu use case. Choose wisely.
---

## Workspace and Source Directory Layout Complexity

Due to the various workspace and source directory placement options and their interactions, path references in `workspace_manager.py` can become complex and confusing.

For a detailed explanation of this situation, recommended usage patterns, and guidance on managing hidden vs. public workspaces and source directories, please see the dedicated documentation file:

**[Workspace and Source Layout Complexity — mulch-layout.md](docs/mulch-layout.md)**

This document provides an in-depth discussion and best practices to help you navigate these nuances.

