param (
    [string]$path
)

#Write-Host "OK"

#Add-Type -AssemblyName PresentationFramework
#[System.Windows.MessageBox]::Show("mulch will run in:`n$path")

if (-Not (Test-Path -Path $path)) {
    [System.Windows.MessageBox]::Show("❌ Path not found:`n$path", "Mulch Init Error")
    exit 1
}

Set-Location -Path $path

# Optional: Add the pipx bin path if needed
$env:PATH += ";$env:USERPROFILE\.local\bin"

# Run mulch init
mulch init --here # --enforce-mulch-folder