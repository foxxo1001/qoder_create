param([Parameter(Mandatory=$true)][string]$Root)
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path -LiteralPath $Root).Path
$py = (Get-Command pythonw.exe -ErrorAction Stop).Source
$script = Join-Path $root 'tools\elens_bridge.py'
$handler = Join-Path $root 'tools\start-bridge.ps1'
if (-not (Test-Path -LiteralPath $script)) { throw "Bridge script not found: $script" }
if (-not (Test-Path -LiteralPath $handler)) { throw "Handler script not found: $handler" }

$classes = 'HKCU:\Software\Classes\elens'
New-Item -Path $classes -Force | Out-Null
Set-ItemProperty -Path $classes -Name '(Default)' -Value 'URL:EmbeddedLens Bridge'
New-ItemProperty -Path $classes -Name 'URL Protocol' -Value '' -PropertyType String -Force | Out-Null
$iconKey = Join-Path $classes 'DefaultIcon'
New-Item -Path $iconKey -Force | Out-Null
Set-ItemProperty -Path $iconKey -Name '(Default)' -Value ($py + ',0')
$cmdKey = Join-Path $classes 'shell\open\command'
New-Item -Path $cmdKey -Force | Out-Null
$powershell = (Get-Command powershell.exe -ErrorAction Stop).Source
$command = '"' + $powershell + '" -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File "' + $handler + '"'
Set-ItemProperty -Path $cmdKey -Name '(Default)' -Value $command
Write-Host "Protocol installed: elens://start (on-demand, no autostart)"
try {
    Start-Process -FilePath $powershell -ArgumentList @('-NoProfile','-WindowStyle','Hidden','-ExecutionPolicy','Bypass','-File','"' + $handler + '"') -WindowStyle Hidden
    Write-Host "Bridge start requested (it will exit after 30 minutes idle)."
} catch {
    Write-Host "Bridge did not start automatically: $($_.Exception.Message)"
}
Write-Host "Open the page and use One-click Read / Launch Helper. Uninstall with uninstall-lens.cmd."