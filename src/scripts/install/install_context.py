import subprocess
from pathlib import Path
import sys
import os

def setup():
    platform = sys.platform
    if platform.startswith("win"):
        # Windows: run your PowerShell script to set registry keys
        ps1_path = Path(__file__).parent / "setup.ps1"
        subprocess.run([
            "powershell.exe",
            "-ExecutionPolicy", "Bypass",
            "-File",
            str(ps1_path)
        ], check=True)
    elif platform.startswith("linux"):
        # Linux: set up Thunar or other desktop environment's context menu
        thunar_action_dir = Path.home() / ".local/share/file-manager/actions"
        thunar_action_dir.mkdir(parents=True, exist_ok=True)
        desktop_file_src = Path(__file__).parent / "mulch-workspace.desktop"
        desktop_file_dest = thunar_action_dir / "mulch-workspace.desktop"
        desktop_file_src.replace(desktop_file_dest)  # or use shutil.copy2()
        print(f"Installed mulch context menu to {desktop_file_dest}")
        
        # provide the .desktop file with executable permissions
        os.chmod(desktop_file_dest, 0o755)
    elif platform == "darwin":
        # macOS: Setup Finder Service or context menu item
        # Could be an Automator workflow or AppleScript installation
        print("macOS detected: implement context menu setup (Automator or Finder Service)")
        print("""Steps:\n 1. Create an Automator Quick Action that runs a shell command or script.\n 2.Export it and install it under ~/Library/Services.\n 3. Optionally, trigger via AppleScript or CLI to register it.
        """)
        # Possibly run an AppleScript or Automator CLI here
    else:
        raise RuntimeError(f"Unsupported platform for setup: {platform}")

if __name__ == "__main__":
    setup()

