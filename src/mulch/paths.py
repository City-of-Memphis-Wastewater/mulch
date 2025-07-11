# src.mulch.paths.py
from pathlib import Path
class MulchPaths:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.dot_mulch = self.root / ".mulch"
        self.scaffold_default = self.dot_mulch / "mulch-scaffold.json"
        self.logs_dir = self.dot_mulch / "logs"
        self.lockfile = self.dot_mulch / "mulch.lock"
