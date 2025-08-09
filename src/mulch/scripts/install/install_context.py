import typer
import subprocess
from pathlib import Path
import sys
import os
import shutil

app = typer.Typer(help="Manage mulch context menu installation")

def setup():
    platform = sys.platform
    if platform.startswith("win"):
        ps1_path = Path(__file__).parent / "setup.ps1"
        if ps1_path.exists():
            subprocess.run([
                "powershell.exe",
                "-ExecutionPolicy", "Bypass",
                "-File",
                str(ps1_path)
            ], check=True)
        else:
            print("Skipping mulch context menu installation (setup.ps1 file not  found).")
    elif platform.startswith("linux"):
        thunar_action_dir = Path.home() / ".local/share/file-manager/actions"
        thunar_action_dir.mkdir(parents=True, exist_ok=True)
        desktop_file_src = Path(__file__).parent / "mulch-workspace.desktop"
        if desktop_file_src.exists():
            desktop_file_dest = thunar_action_dir / "mulch-workspace.desktop"
            # Use copy2 to preserve metadata
            shutil.copy2(desktop_file_src, desktop_file_dest)
            os.chmod(desktop_file_dest, 0o755)
            print(f"Installed mulch context menu to {desktop_file_dest}")
        else:
            print("Skipping mulch context menu installation (no .desktop file found).")
    elif platform == "darwin":
        print("macOS detected: please implement context menu setup via Automator or Finder Service")
        # You can extend this with AppleScript or Automator commands here
    else:
        raise RuntimeError(f"Unsupported platform for setup: {platform}")

@app.command()
def context():
    """Install the mulch workspace right-click context menu."""
    setup()

if __name__ == "__main__":
    app()
