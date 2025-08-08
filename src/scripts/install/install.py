import subprocess
import os

def setup():
    # Locate the setup.ps1 file relative to this script
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    setup_ps1 = os.path.join(repo_root, "scripts", "install", "setup.ps1")

    # Run the PowerShell script with execution policy bypass
    subprocess.run([
        "powershell.exe",
        "-ExecutionPolicy", "Bypass",
        "-File", setup_ps1
    ], check=True)
