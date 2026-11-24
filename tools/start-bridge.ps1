$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$health = 'http://127.0.0.1:8765/health'
try {
    $r = Invoke-WebRequest -UseBasicParsing -TimeoutSec 1 $health
    if ($r.StatusCode -eq 200) { exit 0 }
} catch { }
$py = (Get-Command pythonw.exe -ErrorAction Stop).Source
$script = Join-Path $root 'tools\elens_bridge.py'
$log = Join-Path $root 'tools\bridge.log'
Start-Process -FilePath $py -ArgumentList @('"' + $script + '"', '--log', '"' + $log + '"', '--idle-timeout', '1800') -WorkingDirectory $root -WindowStyle Hidden