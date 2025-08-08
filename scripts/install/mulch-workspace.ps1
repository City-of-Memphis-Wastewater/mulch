param (
    [string]$path
)

if (-Not (Test-Path -Path $path)) {
    [System.Windows.MessageBox]::Show("❌ Path not found:`n$path", "mulch workspace Error")
    exit 1
}

Set-Location -Path $path

## Where does mulch.exe live on a Windows system
$env:PATH += ";$env:USERPROFILE\.local\bin"

## Run mulch init
mulch workspace --here --pattern new # --pattern date

# Start-Sleep -Seconds 1