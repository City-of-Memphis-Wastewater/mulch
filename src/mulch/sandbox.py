def evaluate_workspace_status(self) -> bool:
    if self.workspace_dir.exists():
        if self.space_lock_path.exists():
            try:
                with open(self.space_lock_path, "r", encoding="utf-8") as f:
                    existing = json.load(f)
                if existing.get("scaffold", {}) == self.lock_data["scaffold"]:
                    typer.secho("✅ Scaffold matches existing workspace. Nothing regenerated.", fg=typer.colors.BLUE)
                    return False
                else:
                    typer.confirm(
                        "⚠️ Workspace exists, but scaffold has changed.\nOverwrite workspace?",
                        abort=True
                    )
            except Exception as e:
                typer.confirm(
                    f"⚠️ Workspace exists but space.lock could not be read ({e}).\nOverwrite workspace?",
                    abort=True
                )
        else:
            typer.confirm(
                "⚠️ Workspace exists but no space.lock was found.\nOverwrite workspace?",
                abort=True
            )
    return True

def evaluate_manager_status(self) -> bool:
    if self.bare or self.here:
        return True  # Skip entirely

    if self.manager_lock_path.exists():
        try:
            with open(self.manager_lock_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
            existing_scaffold = existing.get("scaffold", {})
            if existing_scaffold != self.lock_data["scaffold"]:
                typer.confirm(
                    "⚠️ Your current scaffold differs from the one used to generate workspace_manager.py.\n"
                    f"Existing: {self.manager_lock_path}\nContinue?", abort=True
                )
        except Exception as e:
            logging.warning(f"Could not read manager.lock for comparison: {e}")
