# mulch/reg-backup.py
import os

# Use LocalAppData for script location
local_app_data = os.environ['LOCALAPPDATA']
call_script = os.path.join(local_app_data, 'mulch', 'call-mulch-workspace.ps1')

# Commands for context menus
background_command = f'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "{call_script}" "%V"'
folder_command = f'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "{call_script}" "%L"'

# Backup .reg content
reg_content = f"""Windows Registry Editor Version 5.00

; Right-click background of a folder
[HKEY_CURRENT_USER\\Software\\Classes\\Directory\\Background\\shell\\mulch_workspace]
@="mulch workspace"
"Icon"="%LOCALAPPDATA%\\\\mulch\\\\mulch-icon.ico"
"Position"="Top"
"CommandFlags"=dword:00000000
[HKEY_CURRENT_USER\\Software\\Classes\\Directory\\Background\\shell\\mulch_workspace\\command]
@="{background_command}"

; Right-click ON folder
[HKEY_CURRENT_USER\\Software\\Classes\\Directory\\shell\\mulch_workspace]
@="mulch workspace"
"Icon"="%LOCALAPPDATA%\\\\mulch\\\\mulch-icon.ico"
"Position"="Top"
"CommandFlags"=dword:00000000
[HKEY_CURRENT_USER\\Software\\Classes\\Directory\\shell\\mulch_workspace\\command]
@="{folder_command}"
"""

# Ensure backup folder exists
backup_dir = os.path.join(local_app_data, 'mulch')
os.makedirs(backup_dir, exist_ok=True)

# Write the .reg file
backup_path = os.path.join(backup_dir, "mulch_context_backup.reg")
with open(backup_path, "w", encoding="utf-16") as f:
    f.write(reg_content)

print(f"Backup .reg file created at: {backup_path}")
