# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

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


## [0.1.35] – 2025-07-07
### Added
- Notes and logging setup to `WorkspaceManager`.

### Changed
- Improved logging structure.
- Adjusted folder generation logic.

---

## [0.1.9] – 2025-07-03

### Added
- Initial release with basic `mulch init` and JSON-based scaffolding.