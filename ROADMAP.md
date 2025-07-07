- Support for nested folder paths in `mulch-scaffold.json`.
- Initial test suite using `pytest` and `click.testing`.
- Type annotations for public API.

# 🌱 Mulch Roadmap

**Last updated:** July 7, 2025

Welcome to the Mulch project roadmap! This document outlines where the project is headed, what features we're planning, and how you can help shape the journey.

---

## 🌟 Vision

Mulch is a fast, flexible scaffolding CLI for Python (and beyond). It helps you spin up clean, consistent project structures with one command—without needing to start from scratch every time.

Our goal is to make `mulch init` the best "starter kit" CLI for real-world development.

---

## 🚧 In Progress

These features are currently being developed or actively discussed:

- [ ] Clarity for nested folder paths in `mulch-scaffold.json`
- [ ] Consider moving to a `mulch-scaffold.toml` standard, to include helpful comments and instructions.
- [ ] Basic test suite for CLI and config parsing
- [ ] Use and test generated introspective WorkspaceManager classes for passing imports, exports, configs, etc, to ensure stability.
- [ ] First version of contributor docs (`CONTRIBUTING.md`, templates)

---

## 🧭 Planned for `1.0.0`

These are the milestones we want to hit before releasing `v1.0.0`:

### ✨ Features
- [ ] Validate `mulch-scaffold.json` with clear errors
- [ ] Solidify the `mulch-scaffold.json` nesting structure, backed up with clear documentation.
- [ ] Allow `.yaml` and `.toml` config as an alternative to JSON
- [ ] Inline documentation for scaffold files

### 🔐 Stability & Testing
- [ ] Lock down the `WorkspaceManager` API, with features for library import and scripting.
- [ ] CLI regression tests using `pytest` + `click.testing`
- [ ] Add `py.typed` marker for better editor support

### 📦 Project Health
- [ ] Complete `CHANGELOG.md` and semver versioning
- [ ] Setup GitHub Actions for CI
- [ ] Contributor guide + issue templates

---

## 💡 Ideas for the Future

These are not commitments, but open ideas we’re exploring:

- [ ] Includes standard template choices for `mulch-scaffold.json`, for various expected project types. 
- [ ] Jinja2-style variable substitution in templates, for distributable files in a `root/.mulch` file.
- [ ] `mulch add` command for inserting modules into an existing scaffold.
- [ ] VS Code extension for scaffold previews?

Have an idea? Open a [Discussion](https://github.com/city-of-memphis-wastewater/mulch/discussions) or [issue](https://github.com/city-of-memphis-wastewater/mulch/issues)!

---

## 🙋 How to Get Involved

- Want to help implement something above? Comment on the issue or open a PR!
- Not sure where to start? Try an issue labeled `good first issue`
- Just have questions? Reach out via [Discussions](...) or open an issue

Thanks for helping grow Mulch 🌱