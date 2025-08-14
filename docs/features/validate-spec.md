# mulch/docs/features/validate-spec.md
# mulch validate — Specification

## Purpose
`mulch validate` checks the **active** or **specified** workspace against the scaffold (`mulch.toml`) and lock files, reporting any mismatches in structure, required files, or config schema.  
It **does not modify** files by default.

---

## CLI Signature

```bash
mulch validate [--workspace <path_or_name>] [--strict] [--fix] [--schema-only] [--no-schema] [--json]
