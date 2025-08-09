<#
# Usage
## Build for userprofile
.\build-local-mulch-dir.ps1 -Location userprofile

## Build for localappdata
.\build-local-mulch-dir.ps1 -Location localappdata
#>

param (
    [ValidateSet("userprofile", "localappdata")]
    [string]$Location = "userprofile"
)

# Resolve target path based on parameter
switch ($Location) {
    "localappdata" { $targetPath = "$env:LOCALAPPDATA\mulch" }
    "userprofile" { $targetPath = "$env:USERPROFILE\.mulch" }
}

# Create folder if missing
if (-Not (Test-Path $targetPath)) {
    Write-Host "Creating directory $targetPath"
    New-Item -Path $targetPath -ItemType Directory -Force | Out-Null
} else {
    Write-Host "Directory $targetPath already exists"
}

# Copy relevant files from current directory to target
$filesToCopy = @(
    "call-mulch-workspace.ps1",
    "mulch-workspace.ps1",
    "mulch-icon.ico",
    "install-mulch-workspace-userprofile.reg",
    "install-mulch-workspace-localappdata.reg"
)

foreach ($file in $filesToCopy) {
    if (Test-Path $file) {
        Copy-Item -Path $file -Destination $targetPath -Force
        Write-Host "Copied $file to $targetPath"
    } else {
        Write-Warning "File $file not found in current directory"
    }
}
