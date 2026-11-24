$ErrorActionPreference = 'Stop'
$lnk = Join-Path ([Environment]::GetFolderPath('Startup')) 'EmbeddedLens Bridge.lnk'
if (Test-Path -LiteralPath $lnk) {
    Remove-Item -LiteralPath $lnk -Force
    Write-Host "Removed legacy autostart: $lnk"
} else {
    Write-Host "No autostart entry found (on-demand mode)."
}
$classes = 'HKCU:\Software\Classes\elens'
if (Test-Path -LiteralPath $classes) {
    Remove-Item -LiteralPath $classes -Recurse -Force
    Write-Host "Removed protocol: elens://"
} else {
    Write-Host "Protocol is not installed."
}