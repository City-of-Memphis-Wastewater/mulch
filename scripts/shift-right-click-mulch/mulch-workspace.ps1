param (
    [string]$path
)

if (-Not (Test-Path -Path $path)) {
    [System.Windows.MessageBox]::Show("❌ Path not found:`n$path", "mulch workspace Error")
    exit 1
}

Set-Location -Path $path

# Where does mulch.exe live on a Windows system
$env:PATH += ";$env:USERPROFILE\.local\bin"

# make this path if it does not exsit, and inject the mulch-icon.ico file and the mulch-workspace.ps1 file
#";$env:USERPROFILE\.mulch"

# Run mulch init
mulch workspace --pattern new --here # --pattern date