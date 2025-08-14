
### mulch/docs/features/show-spec.md

# mulch show — Specification

## Purpose
Display the contents of the first available scaffold, or a scaffold by index, in plain text.

---

## CLI Signature
```bash
mulch show [<index>] [--target-dir <path>]
````

### Inputs

| Parameter / Flag      | Meaning                                                              |
| --------------------- | -------------------------------------------------------------------- |
| `index`               | Numeric index (from `mulch order`) indicating which scaffold to show |
| `--target-dir` (`-t`) | Project root directory (defaults to cwd)                             |

---

## Behavior

1. If `index` is provided:

   * Select that source (fallback if needed).
2. Otherwise:

   * Use the first found scaffold in order of respect.
3. Load the `.toml` content and print it to stdout.
4. If none found: exit with error.

---

## Outputs

* Prints the scaffold contents in TOML format.
* Precedes with a line indicating “Loaded scaffold from ...”

---

## Exit Codes

* `0`: Success.
* Non-zero: Index out of range or no scaffold found.
