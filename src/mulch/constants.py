import toml
DEFAULT_SCAFFOLD_FILENAME = "mulch.toml"

LOCK_FILE_NAME = 'mulch.lock'

FALLBACK_SCAFFOLD_JSON = {
        "": ["scripts", "tools", "templates", "exports", "imports", "images", "documents", "configurations", "about_this_workspace.md"],
        "exports": ["aggregate"],
        "configurations": ["default-workspace.toml", "logging.json"],
        "secrets": ["to-be-run-at-creation.yaml"],
        "tools": ["to-be-used-as-needed.toml"]
    }

FALLBACK_SCAFFOLD_TOML = '''[scaffold]
dirs = [
    "data",
    "data/raw",
    "data/processed/monthly",
    "queries/historical/archive",
]
files = [
    "queries/historical/default-queries.toml",
    "data/processed/monthly/README.md",
    "secrets/secrets-example.yaml"
]'''
FALLBACK_SCAFFOLD = toml.loads(FALLBACK_SCAFFOLD_TOML)

'''EXAMPLE
data = {
    "section": {
        "key": "value",
        "list": [1, 2, 3],
        "subsection": {
            "foo": "bar"
        }
    }
} 

with open("file.toml", "w") as f:
    toml.dump(data, f)

[section]
key = "value"
list = [1, 2, 3]

[section.subsection]
foo = "bar"
'''