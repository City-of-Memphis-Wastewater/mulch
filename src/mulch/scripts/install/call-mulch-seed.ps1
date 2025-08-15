$folder = $args[0]
Start-Process powershell -ArgumentList @('-ExecutionPolicy', 'Bypass', '-File', "$PSScriptRoot\mulch-seed.ps1", "`"$folder`"") -NoNewWindow -Wait
