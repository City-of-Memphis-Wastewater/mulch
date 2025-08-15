param (
    [string]$path
)

if (-Not (Test-Path -Path $path)) {
    Write-Error "Path not found: $path"
    return
}

Write-Output "Processing path: $path"

Set-Location -Path $path

## Where does mulch.exe live on a Windows system
$env:PATH += ";$env:USERPROFILE\.local\bin"

## call mulch seed, to build new .mulch folder, to generate .mulch/mulch.toml using the most available fallback, and to open mulch.toml for editing.
mulch seed 	

Read-Host -Prompt "Press Enter to exit"