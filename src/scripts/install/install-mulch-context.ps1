# Define paths
$localAppDataPath = "$env:LOCALAPPDATA\mulch"
$userProfilePath = "$env:USERPROFILE\.mulch"

if (Test-Path "$localAppDataPath\call-mulch-workspace.ps1") {
    $regFile = "install-mulch-workspace-localappdata.reg"
	$targetPath = $localAppDataPath
} elseif (Test-Path "$userProfilePath\call-mulch-workspace.ps1") {
    $regFile = "install-mulch-userprofile.reg"
	$targetPath = $userProfilePath
} else {
    # Default to userprofile path
    $regFile = "install-mulch-workspace-userprofile.reg"
	
    # Create folder if not exists
    if (-Not (Test-Path $userProfilePath)) {
        New-Item -Path $userProfilePath -ItemType Directory -Force
    }
	$targetPath = $userProfilePath
}

# Copy files from installer directory (assumes script is run from source folder)
Copy-Item -Path ".\call-mulch-workspace.ps1" -Destination $targetPath -Force
Copy-Item -Path ".\mulch-workspace.ps1" -Destination $targetPath -Force
Copy-Item -Path ".\mulch-icon.ico" -Destination $targetPath -Force
Copy-Item -Path ".\install-mulch-workspace-userprofile.reg" -Destination $targetPath -Force
Copy-Item -Path ".\install-mulch-workspace-localappdata.reg" -Destination $targetPath -Force

# Run the selected registry import
Start-Process reg.exe -ArgumentList "import `"$regFile`"" -Verb RunAs -Wait
