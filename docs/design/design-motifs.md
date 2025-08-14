# mulch/docs/design/design-motifs.md
# Design Motifs

Mulch borrows ideas from version control, environment management, and saved game systems to create a consistent, switchable workspace environment.

---

## 🎯 Core Concept

Mulch treats **workspace context** like a “save slot” in a video game:

- **Git** saves your source code history.
- **Conda** saves your dependency environment.
- **Mulch** saves your *project state* — folder layout, configuration files, and local resources — without altering code or dependencies.

A **workspace** is just a folder hierarchy with a known schema, which can be swapped in/out for different contexts or projects.  
A **scaffold** defines that schema, and a **lock file** pins it to a specific version.

---

## 🧩 Principles

1. **Convention over configuration**  
   Folder and file layout is consistent across all workspaces for a given project. This means tools, scripts, and teammates can rely on paths without guesswork.

2. **Read-only schema**  
   Mulch never changes your source code or dependencies. It only manages and validates workspace data.

3. **Declarative scaffolding**  
   The scaffold (`mulch.toml`) describes the expected structure. Workspaces can be created, validated, or fixed based on this declaration.

4. **Portable state**  
   Workspaces are ASCII-encoded and can be committed to version control or moved between systems.

5. **Composable tooling**  
   Mulch does not replace Git, Conda, or Docker — it works alongside them.

---

## 🔄 How it Fits with Other Tools

| Tool   | Scope Managed           | Analogy         |
|--------|------------------------|----------------|
| Git    | Source code history    | The “game’s” code |
| Conda  | Dependency environment | The “console”   |
| Mulch  | Workspace state        | The “save file” |

---

## 🧪 Validation as a First-Class Citizen

A scaffold is only useful if it’s enforced. Mulch aims to:

- Provide `mulch validate` for checking current workspace integrity
- Optionally fix missing parts with `--fix`
- Support schema-based config validation (via pydantic, JSON Schema, etc.)

---

## 🚀 Future Ideas

- Database-backed workspace registry with history tracking
- Alternate scaffolds for different workflow modes
- Integration with CI pipelines for automated workspace validation
- Schema tags for partial validation

---

Mulch is meant to be **minimal but strict where it counts**, giving you a reliable project state without locking you into a heavyweight workflow.
