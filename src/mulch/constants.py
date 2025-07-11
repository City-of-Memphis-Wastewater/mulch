
DEFAULT_SCAFFOLD_FILENAME = "mulch-scaffold.json"

LOCK_FILE_NAME = 'mulch.lock'

FALLBACK_SCAFFOLD = {
        "": ["config", "docs", "imports", "exports", "scripts", "secrets", "queries","about_this_workspace.md"],
        "exports": ["aggregate"],
        "config": ["default-workspace.toml", "logging.json"],
        "secrets": ["secrets-example.yaml"],
        "queries": ["default-queries.toml"]
    }