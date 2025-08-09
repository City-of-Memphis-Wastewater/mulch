# Define paths
$localAppDataPath = "$env:LOCALAPPDATA\mulch"
$userProfilePath = "$env:USERPROFILE\.mulch"

if (Test-Path "$localAppDataPath\call-mulch-workspace.ps1") {
	$regFile    = Join-Path $localAppDataPath "install-mulch-workspace-localappdata.reg"
	$targetPath = $localAppDataPath
} elseif (Test-Path "$userProfilePath\call-mulch-workspace.ps1") {
	$regFile    = Join-Path $userProfilePath "install-mulch-workspace-userprofile.reg"
	$targetPath = $userProfilePath
} else {
    Write-Error "No mulch installation found in either $localAppDataPath or $userProfilePath. 
Please run build-local-mulch-dir.ps1 first.
install.py calls setup.ps1, which calls build-local-mulch-dir.ps1.
To run the setup() function in  install.py, call `poetry run mulch-setup`, if installing from the git-cloned source. Or, more likely, re-run `pipx install mulch`."
    exit 1
}

# Run the selected registry import
#Start-Process reg.exe -ArgumentList "import `"$regFile`"" -Wait
reg import "$regFile"
