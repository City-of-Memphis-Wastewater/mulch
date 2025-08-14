### mulch/docs/features/src-spec.md

# mulch src — Specification

## Purpose
Generate Python helper source (workspace_manager) based on current (or referenced) workspace and scaffold, for convenient access in project code.

---

## CLI Signature
```bash
mulch src [--target-dir <path>] [--stealth] [--force] [--wrkspc-in-root/--wrkspc-in-wrkspc] [--name <src_name>]
````

### Inputs

| Flag                                      | Meaning                                                                                                        |
| ----------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| `--target-dir` (`-r`)                     | Project root directory (defaults to cwd)                                                                       |
| `--stealth` (`-s`)                        | Place generated source under `.mulch/src/` instead of `src/`                                                   |
| `--force`                                 | Overwrite existing sources without prompt                                                                      |
| `--wrkspc-in-root` / `--wrkspc-in-wrkspc` | Control how `ReferenceLockManager` records workspace reference — if running before any workspace is registered |
| `--name` (`-n`)                           | Override the default name used in source paths                                                                 |

---

## Behavior

1. Ensure `mulch workspace` has run previously (especially needed when using stealth).
2. Possibly initialize `.mulch` if missing.
3. Resolve scaffold and workspace references.
4. Write `workspace_manager.py` source file into the project following flags.
5. Update the src reference lock.

---

## Outputs

* A generated source module (`workspace_manager.py`), placed under configured path.
* Updated reference lock for the src (`.mulch/reference.lock` updated).

---

## Exit Codes

* `0`: Success.
* Non-zero: Workspace not registered, write error, or invalid flags.


