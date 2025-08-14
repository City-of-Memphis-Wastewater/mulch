### mulch/docs/features/context-spec.md

# mulch context — Specification

## Purpose
Install a context-menu integration (OS-specific). Enables right-click "Mulch workspace" actions.

---

## CLI Signature
```bash
mulch context
````

### Inputs

* No flags or parameters.

---

## Behavior

1. Call `install_context.setup()` to configure OS context-menu (Windows registry, etc.).

---

## Outputs

* OS-level context menu item installed.
* No output unless errors or logging messages.

---

## Exit Codes

* `0`: Success.
* Non-zero: OS integration errors (permissions, unsupported platform).

