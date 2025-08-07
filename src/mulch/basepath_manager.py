from pathlib import Path
class PathContext:
    def __init__(self,
                 base_path: Path,
                 workspace_name: str,
                 *,
                 here: bool = False,
                 stealth: bool = False):
        self.base_path = base_path
        self.workspace_name = workspace_name
        self.here = here
        self.stealth = stealth

    @property
    def workspace_dir(self) -> Path:
        if self.here or self.stealth:
            return self.base_path / self.workspace_name
        return self.base_path / "workspaces" / self.workspace_name

    @property
    def source_dir(self) -> Path:
        if self.stealth:
            return self.base_path / ".mulch" / "src"
        return self.base_path / "src"

    @property
    def module_dir(self) -> Path:
        return self.source_dir / self.base_path.name

    @property
    def manager_path(self) -> Path:
        return self.module_dir / "workspace_manager.py"
    
    @property
    def manager_lock_path(self) -> Path:
        return self.module_dir / "manager.lock"
    
    @property
    def workspace_lock_path(self) -> Path:
        return self.workspace_dir / "space.lock"
    
    @property
    def flags_lock_path(self) -> Path:
        return self.base_path / ".mulch" / "flags.lock"