### mulch/docs/features/order-spec.md

# mulch order — Specification

## Purpose
Display the ordered list of possible scaffold sources (project local, user, system, fallback) and indicate which ones exist.

---

## CLI Signature
```bash
mulch order [--target-dir <path>]
````

### Inputs

| Flag                  | Meaning                                  |
| --------------------- | ---------------------------------------- |
| `--target-dir` (`-t`) | Project root directory (defaults to cwd) |

---

## Behavior

1. Evaluate the configured `ORDER_OF_RESPECT` paths.
2. Check for the existence of `mulch.toml` in each path.
3. Output a table indicating index, path, and existence status.

---

## Outputs

* Text listing possible scaffold sources and whether they exist.
* A visual rich table with index, path, and an “exists?” column.

---

## Exit Codes

* `0`: Always returns success (table output).
* Non-zero: Rare—path access errors.

