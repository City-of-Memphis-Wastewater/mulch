# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.2.1->3] - 2025-07-08 -> 2025-07-11

## In Progress
- Really logs should never be generated at root/logs, but at root/.mulch/logs. mulch-scaffold.toml/.json is the only file that might be nice at the top level. 

## Changes:
- Include verbose tag to `twine upload --repository testpypi dist/* --verbose` in `test-build.yml`
- Refactor and migration of several functions internal to the internal cli.py to now be class functions in the WorkspaceFactory class.
- Change `dotmulch` command to `seed`. Formerly: `folder` or `dotfolder`.

## Added:
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