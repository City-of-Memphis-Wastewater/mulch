
# mulch/docs/features/seed-spec.md
# mulch seed — Specification

## Purpose
Create or update the project scaffold (`.mulch/mulch.toml`) at the target directory, sourcing from configured templates or the embedded fallback.

---

## CLI Signature
```bash
mulch seed [--target-dir <path>] [--index <n>] [--template-choice <choice>] [--edit]
````

### Inputs

| Flag                       | Meaning                                                                 |
| -------------------------- | ----------------------------------------------------------------------- |
| `--target-dir` (`-t`)      | Directory in which to create `.mulch` folder (`.` if omitted)           |
| `--index` (`-i`)           | Numeric index to select scaffold source as listed by `mulch order`      |
| `--template-choice` (`-c`) | Template key from known template dictionary *(currently unimplemented)* |
| `--edit` (`-e`)            | Opens the scaffold file in an editor after writing it                   |

---

## Behavior

1. Determine scaffold source based on `--index`, `--template-choice`, or first valid source in order of respect, falling back to embedded `FALLBACK_SCAFFOLD`.
2. Write scaffold file to `<target-dir>/.mulch/mulch.toml`, prompting if it exists.
3. Optionally open the file in editor if `--edit` is used (or confirmed).

---

## Outputs

* `.mulch/mulch.toml` created/updated.
* If editor invoked, your default editor opens the scaffold.

---

## Exit Codes

* `0`: Success.
* Non-zero: Missing scaffold source, invalid index, or write errors.


---

### `docs/features/workspace-spec.md`
```markdown
# mulch workspace — Specification

## Purpose
Initialize or register a new workspace directory based on the scaffold, optionally registering it as the default.

---

## CLI Signature
```bash
mulch workspace [--target-dir <path>] [--pattern <date|new>] [--name <workspace_name>] [--here] [--set-default/--no-set-default]
````

### Inputs

| Flag                                 | Meaning                                                                              |
| ------------------------------------ | ------------------------------------------------------------------------------------ |
| `--target-dir` (`-r`)                | Project root directory (defaults to cwd)                                             |
| `--pattern`                          | Workspace naming strategy: `date` (timestamp) or `new` (OS-style "New workspace")    |
| `--name` (`-n`)                      | Explicit workspace name                                                              |
| `--here` (`-h`)                      | Create the workspace directory directly under project root rather than `workspaces/` |
| `--set-default` / `--no-set-default` | Whether to write a `default-workspace.toml` file to mark this workspace as default   |

---

## Behavior

1. Determine `workspaces` directory using `WorkspaceInstanceFactory`.
2. Generate workspace name via pattern or explicit `--name`.
3. Ensure a `.mulch` exists in the project; if not, create it.
4. Resolve scaffold to build directory tree.
5. Compare to existing workspace (if any): match, differs, or missing lock.
6. Prompt for overwrite if scaffold changed or no lock exists.
7. Create workspace directory based on the scaffold.
8. Update the reference lock to point to the new workspace.
9. Write default workspace file if `--set-default`.

---

## Outputs

* A new workspace directory with scaffold structure.
* Updated reference lock (`.mulch/reference.lock`).
* `default-workspace.toml` if `--set-default`.

---

## Exit Codes

* `0`: Success.
* Non-zero: Prompt aborted, write error, or invalid flags.


---

