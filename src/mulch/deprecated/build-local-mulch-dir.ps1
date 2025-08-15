# src/mulch/scripts/install/build-local-mulch-dir.ps1
<#
# Usage
## Build for localappdata
.\build-local-mulch-dir.ps1
#>
# Set location to the script's own directory
Set-Location -Path $PSScriptRoot
# Set the target path for the local mulch directory
$targetPath = "$env:LOCALAPPDATA\mulch" # hardcoded path for "LocalAppData/mulch", preferred over USERPROFILE so that we do allow the user to conflate the meaning of "%USERPROFILE%/.mulch" as a configuration directory rather than seeded dotmulch directory

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
    "mulch-icon.ico"
)

foreach ($file in $filesToCopy) {
    if (Test-Path $file) {
        Copy-Item -Path $file -Destination $targetPath -Force
        Write-Host "Copied $file to $targetPath"
    } else {
        Write-Warning "File $file not found in current directory"
    }
}
