# Changelog
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.2.9] - 2025-07-20

### Fixes
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