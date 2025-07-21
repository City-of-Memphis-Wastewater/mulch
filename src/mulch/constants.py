
DEFAULT_SCAFFOLD_FILENAME = "mulch.toml"

LOCK_FILE_NAME = 'mulch.lock'

FALLBACK_SCAFFOLD = {
        "": ["scripts", "tools", "templates", "exports", "imports", "images", "documents", "configurations", "about_this_workspace.md"],
        "exports": ["aggregate"],
        "configurations": ["default-workspace.toml", "logging.json"],
        "secrets": ["to-be-run-at-creation.yaml"],
        "tools": ["to-be-used-as-needed.toml"]
    }