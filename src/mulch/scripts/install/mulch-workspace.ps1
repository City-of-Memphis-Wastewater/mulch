param (
    [string]$path
)

#if (-not $path) {
#	$path = Get-Location
#}

if (-Not (Test-Path -Path $path)) {
    Write-Error "Path not found: $path"
    return
}

Write-Output "Processing path: $path"

Set-Location -Path $path

## Where does mulch.exe live on a Windows system
$env:PATH += ";$env:USERPROFILE\.local\bin"

## Run mulch src
mulch workspace --here --pattern new # --pattern date

#Start-Sleep -Seconds 4
Read-Host -Prompt "Press Enter to exit"