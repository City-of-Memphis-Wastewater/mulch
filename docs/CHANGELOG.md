# Changelog
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.2.41] - 2025-08-11

### Fixed
- Remove calculations for `manager_path` and `manager_lock_path` in `WorkspaceInstanceFactory`; these were a holdover from when deprecated `mulch init` split into `mulch src` and `mulch workspace`.
- Change the order of code in the CLI `workspace` command, such that build_flags_record() is called before the defaults are assigned.
---

## [0.2.40] - 2025-08-11

### Added
- `mulch src` now hase a `--name` flag, to enable source code folder names that do not have the same name as the base_dir. Non-matching names are successfully recorded in the `.mulch/reference.lock file.`

### Fixed
- `basepath_manager.py` modularized to accept various `project_name` vars, to accomodate the `--name` flag in `mulch src`

---

## [0.2.36] - 2025-08-11

### Added
- Support for multiple `src` instances in `reference.lock` with `"instances"` list.
- `list_src()` and `list_workspaces()` methods added to `ReferenceLockManager` for listing registered instances.
- Improved handling of duplicate `src` and workspace paths with flag overwriting.
- Optional metadata embedding per workspace and src instance considered for more granular tracking.

### Changed
- `"paths"` key renamed to `"instances"` in both `"workspaces"` and `"src"` sections of `reference.lock`.
- Validation and update logic adjusted to match new `instances` schema.
- `build_flags()` function changed to `build_flags_record()`, with more inclusion of flags from both the `src` and `workspace` CLI commands.

### Fixed
- Removed legacy singular `"src.path"` and `"src.flags"` from `reference.lock` to avoid structural conflicts.
- Corrected flag assignment for `src` entries ensuring flags are properly saved and listed.

---

## [0.2.32] - 2025-08-10

### Added
- reference.lock and the relevant reference_lock_manager.py and ReferenceLockManager class. Calls added in cli.py for workspace() and src().

### Breaking Changes
- `--stealth` flag removed from `mulch workspace` command. See README.md and docs/mulch-layout.md for more information.

---

## [0.2.30] - 2025-08-09

### Fixed
- Print statement and help statement improvements.

---

## [0.2.29] - 2025-08-09

### Fixed
- logger.DEBUG() -> logger.debug()

---

## [0.2.27] - 2025-08-09

### Changed
- Improve description in pyproject.toml and on GitHub top level README.md.

---

## [0.2.26] - 2025-08-09

### Fixed
- Remove defunct show_() command.
- Improve print messages

---

## [0.2.25] - 2025-08-09

### Added
- `--force` flag added to `mulch src`.
- mulch show <index> — You can now pass an optional index (from mulch order) to display the scaffold from a specific configuration source, instead of always using the first available in the order of respect.
    - Example: mulch show 3 loads from the third source in the list shown by mulch order.

### Removed
- Comment out the enforce_mulch_folder option in `mulch src`, just as in `mulch workspace`. https://github.com/City-of-Memphis-Wastewater/mulch/issues/10

---

## [0.2.24] - 2025-08-09

### Fixed
- Remove instances of outdated reference `mulch folder` in comments, change to `mulch workspace`.

### Removed
- Comment out the enforce_mulch_folder option in `mulch src`, just as in `mulch workspace`. https://github.com/City-of-Memphis-Wastewater/mulch/issues/10

---

## [0.2.23] - 2025-08-09

### Breaking Changes
- `mulch init` -> `mulch src`. 

### Changed
- Remove `Path('.')` from ORDER_OF_RESPECT.  https://github.com/City-of-Memphis-Wastewater/mulch/issues/9

### Added
- Use 'bootstrapper' in `pyproject.toml` description and `README.md`
- Example in `README.md` to demonstrate the `--pattern` flag in `mulch workspace`

---

## [0.2.22] - 2025-08-09

### Fixed
- Add logic to handle if files to copy and use are not available, in `/src/mulch/scipts/install/install_context.py`  
- Add file references in pyproject.toml include list for the files references in `/src/mulch/scipts/install/build-local-mulch-dir.ps1`  

---

## [0.2.21] - 2025-08-09

### Fixed
- `/src/mulch/scipts/install/.desktop` -> `/src/mulch/scipts/install/mulch-workspace.desktop` 

---

## [0.2.19->0.20.20] - 2025-08-09

### Changed
- `src.mulch.etcetera` references destroyed in favor of just `mulch.etcetera`.
- `scipts/install/` moved from `/src/` to `/src/mulch/`

---

## [0.2.19->0.2.20] - 2025-08-09

### Changed
- Implement the `mulch-context` as its own Tpyer command so that mulch-context shows up properly.

---

## [0.2.18] - 2025-08-09

### Changed
- `mulch order` command is now much more useful. There is a weird bug with the order of repsect list being appended.

---

## [0.2.17] - 2025-08-09

### Changed
- `mulch workspace --pattern new` is back in, `mulch workspace --pattern os` is out.

---

## [0.2.16] - 2025-08-09

### Changed
- `mulch workspace --pattern new` changed to `mulch workspace --pattern os`, for a more memorable tag, infering that the behavior differs for each operating sytem. Using a value like 'new' is confounding, because the Apple standard is 'untitled folder' which can be mimicked as 'untitled workspace'; the Linux and Windows standards both include the word 'New'. 
- `poetry run mulch-setup` is now `poetry run mulch-context`.

### Added 
- The `context` CLI command in `mulch`. This functonality is also leverage by `poetry run mulch-context`.
---

## [0.2.15] - 2025-08-08

### Changed
- The quintessential context menu option for `mulch` now is `mulch workspace`. This calls `mulch-workspace.ps1`. The command is actually `mulch workspace --here --pattern new` 

### Added
- Added `--pattern` flag to `mulch workspace` command, to enable the current data standard as well as `New workspace (3)` standard to mimick windows. This is ideal for the user-facing right click context menu entry.
- implement helpers.get_default_untitled_workspace_name_based_on_operating_system()

### Removed
- Extraneous or outdated .reg files for `mulch` commands  that do not need to be user facing.

### To Do
- Generate the .reg file templated based on user name, to hardcode the path, which is required.
- Add the mulch-icon.ico file, the mulch-workspace.reg file, the mulch-workspace.ps1 file, a mulch.toml scaffold file, and the .mulchvision file to a <user>/AppData/Local/mulch/ directory on Windows, or possibly to /<user>/.mulch. Use the /.mulch folder for Linux.
- Automatically generate these local folders as necessary.
- Develop evaluate_flags_lock_status() to enforce `mulch workspace` consistency as necessary. Is this necessary, if the right click menu is the user facing option? The workspace_manager.py file can only reference one of them. This begs a questions about `mulch init` needing clarity on where the `mulch workspace` folders will go. Or, it can be an input into the calls in 'workspace_manager.py, with a default of the `workspaces` folder in root, but with alternative options as necessary. Let them blow their legs off. In this way, you can have stealth and non-stealth src, and workspace dirs in --here, in --stealth --here, in --stealth, and in `root/workspaces`, if you want; That's the user's business, not mine. But maybe we should warn them to be consistent and let them force?
- We need a `mulch context` command to run the `mulch-workspace.reg` file to install the command the context menu. This will naturally build the user's mulch system folder, wherever it might be (see above).
- `mulch system` or `mulch user` is cool, but then we are really getting busy when we run `mulch --help`
---

## [0.2.14] - 2025-08-07

### Fixed
- Fixed scaffold loading to properly use `FALLBACK_SCAFFOLD_TOML` instead of legacy workspace structure
- Fixed import paths to use `mulch.` instead of `src.mulch.`
- Corrected scaffold file structure in `.mulch/mulch.toml` generation

### Changed
- Improved scaffold file handling with proper TOML/JSON support
- Enhanced logging messages for scaffold loading
- Streamlined scaffold resolution process

### Added
- Better error handling for scaffold file parsing
- More descriptive log messages for scaffold loading steps
- Type hints for scaffold loading functions

### Removed
- Legacy workspace structure fallback
- Redundant scaffold loading functions

The key change in this version is fixing the scaffold structure to properly use the data-centric layout:
```toml
[scaffold]
dirs = [
    "data",
    "data/raw",
    "data/processed/monthly",
    "queries/historical/archive"
]
files = [
    "queries/historical/default-queries.toml",
    "data/processed/monthly/README.md",
    "secrets/secrets
```
## [0.2.12] - 2025-08-07

### Added
- New `create_workspace()` method for cleaner workspace initialization
- Type hints for better code maintainability and IDE support
- Support for both flat and nested scaffold structures
- Better error handling and status reporting

### Changed
- Split `WorkspaceManagerGenerator` and `WorkspaceInstanceFactory` into separate classes
- Improved lock file handling with proper directory creation order
- Better scaffold structure validation
- More consistent path resolution through `PathContext`

### Fixed
- Lock file creation ordering issue
- Proper handling of nested scaffold directories
- Default workspace config file placement
- Double-nested scaffold data parsing

### Removed
- Deprecated initialization methods
- Redundant workspace building functions
- Unused file loader imports

---

## [0.2.9-->0.2.11] - 2025-07-22

### Vibe
- Aside from testing, we have succeeded in changing to TOML mulch.toml standard, and moving away from the mulch-scaffold.json standard. 

### Unfinished
- build_dotmulch_standard_contents() is not yet useful
- `--stealth` flag should also be used for `mulch workspace` command, to build inside of root/.mulch/workspaces/
- We need a way to enforce the `--here` for additional workspaces, if it is forgotten, if it has already been used, or if 	`mulch init --stealth` has been used. Leverage a configuration file in `.mulch` for this.


---

## [0.2.8->0.2.9] - 2025-07-11-->2025-07-20

### Breaking Changes
- split `mulch init` command into `mulch init` and `mulch workspace`
- `_determine_workspace_dir(target_dir, name, here, bare, stealth)` inputs adjusted to `_determine_workspace_dir(target_dir, name, here, stealth)` 

### Fixes
- Address failure to reference anything other than the fallback scaffold; order_of_respect_local = [Path.cwd() / '.mulch']
- Implement `resolve_scaffold()` in `mulch file`. 

### Changes
- `--bare flag removed from both `mulch init` and `mulch workspace` by the nature of what the split represents.
- Remove `bare` implementations in `workspace_factory.py`.

### To docs
- `mulch workspace` should rely on the architecture for its default behavior (here VS standard), which should be represented in a configuration file, like `/root/.mulch/mulch-config.toml`

---

## [0.2.7->0.2.8] - 2025-07-11

### Fixes
- Improved README.md for a polished release.

### Upcoming priority
- Add a command for .reg registry impact for context menu commands, for Windows users. Provide automated Thunar solution as well if possible. Think about the Apple folks and freaks, too.

---

## [0.2.5->0.2.6] - 2025-07-11

### In progress
- mulch.helpers.resolve_scaffold() is vying for power with mulch.workspace_factory.load_scaffold()

### Fixes
- `scaffold_dict = resolve_scaffold(ORDER_OF_RESPECT, FILENAMES_OF_RESPECT)` added to the top of the `seed` CLI command due to failure of the seed command when no scaffold_dict was known. 

### Added
- --edit flag in `mulch seed` and `mulch file`, to launch editor automatically. Otherwise, there is a typer.confirm(). 

---

## [0.2.4] - 2025-07-11

### Added
- `--stealth` tag now can be used with init (`mulch init --stealth`) to alter the basepath for where the workspace manifests (directly in root) and where the workspace_manager is built (in root/.mulch/src/root-name/).
- basepath_manager.py helps to organize path context.

---

## [0.2.1->3] - 2025-07-08 -> 2025-07-11

### In Progress
- Really logs should never be generated at root/logs, but at root/.mulch/logs. mulch-scaffold.toml/.json is the only file that might be nice at the top level. 

### Changes:
- Include verbose tag to `twine upload --repository testpypi dist/* --verbose` in `test-build.yml`
- Refactor and migration of several functions internal to the internal cli.py to now be class functions in the WorkspaceFactory class.
- Change `dotmulch` command to `seed`. Formerly: `folder` or `dotfolder`.

### Added:
- Small `WorkspaceStatus` class in `src.mulch.workspace_status` assists to manager complexity in the CLI init function.Use: `workspace_status = wf.evaluate_workspace_status()`

## [0.1.37] – 2025-07-08

### Fixed
- `Path.cwd()/'placeholder_workspace_dir'` used as a placehold for the `workspace_dir` argument in `WorkspaceFactory`.

### Discourse (not completed)
- Consider adding default args for `WorkspaceFactory` if workspace_dir is not included - to allow for easy placeholders or to not require placeholders. Why? To be able to access class functions without initializing a truly useful `WorkspaceFactory` - or consider moving these functions elsewhere.

## [0.1.37] – 2025-07-08

### Breaking Changes
- `--codeless/-c` flag changed to - `--bare/-b` flag in the init command,	 to keep with expected standards.
- Alter `target_dir` positional argument for init. Implement expicit `--target-root-dir/-r` flag. Command change: typer.Argument() --> typer.Option(). Tested successfully with `poetry run python -m mulch.cli init --name tflag -r root`, which generates a new root target dir, with its own folders for `src`, `workspaces`, and `logs`.
- Add `workspace_dir` value logic to rely on `--here` flag prior to calling `_init_workspace()`; `workspace_dir` and `here` and `bare` are now required inputs for `_init_workspace()`. Also, `workspace dir` is now a required positional input for `WorkspaceFactory()`, because `self.workspace_dir` is assigned directly from the input in `WorkspaceFactory.__init__()`, rather than being calculated duplicately by some Path assignement that includes `/workspaces/`; this relationship only is determined in `workspace_dir = cli._determine_workspace_dir(target_dir, name, here, bare)`. 
	
### Added
- `docs` directory in root. This is meant to be organized and official.
- `research\chatlogs` added in root, for markdown transcripts of brainstorming notes and fact finding with a chat bot.
- `mulch 0.1.36 notes.md`added to `research\chatlogs`
- Create the `--here` flag for the `init` command, to mean that the new named workspace directory should be placed immediately in the current working directory, rather than nested within a `/workspaces/` directory. Enforce that the `--here` flag can only be used with the `--bare` flag.
- `_determine_workspace_dir()` in `cli.py` to determine `workspace_dir` based on `here` flag.
- To minimize user typing and confusion, `bare` value forced to True when `here` is True.
- `.mulch` folder - To configure local rules and templates for any given diretory. `.mulch/HERE` can be `false` or `true` - the default is `false` but the most pertinent use-case is `true`, for non-python users quickly standup new projects without a Pythonic template.

## [0.1.35] – 2025-07-07

### Added
- `--codeless/-c` flag to `mulch init` to skip Python-specific scaffolding. This will allow use for non-software directory scaffolding.  Thanks Michael Gratzer for the parlance brainstorming and contribution.
- CHANGELOG.md
- ROADMAP.md

### Changed
- Minimize use of `logging/logger.info()` in favor of `typer.echo()`, `typer.secho()`, and `logger.debug()`. 
- `WorkspaceManager` now validates config before file creation.
- Improved error messages when `mulch-scaffold.json` is missing or invalid.

### Fixed
- typer.echo() does not handle newline characters as expected. 
- CLI now gracefully handles missing config files.

---


## [0.1.34] – 2025-07-07
### Added
- Notes and logging setup to `WorkspaceManager`.

### Changed
- Improved logging structure.
- Adjusted folder generation logic.

---

## [0.1.9] – 2025-07-03

### Added
- Initial release with basic `mulch init` and JSON-based scaffolding.