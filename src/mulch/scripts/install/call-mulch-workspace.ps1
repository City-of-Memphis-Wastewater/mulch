#Start-Process powershell ` -ArgumentList @("-ExecutionPolicy", "Bypass", "-File", "$PSScriptRoot\mulch-workspace.ps1") ` # -WindowStyle Hidden
#param(
#    [string]$path
#)

#Start-Process powershell -ArgumentList @('-ExecutionPolicy', 'Bypass', '-File', "$PSScriptRoot\mulch-workspace.ps1", $path) -NoNewWindow -Wait

$folder = $args[0]
Start-Process powershell -ArgumentList @('-ExecutionPolicy', 'Bypass', '-File', "$PSScriptRoot\mulch-workspace.ps1", "`"$folder`"") -NoNewWindow -Wait
