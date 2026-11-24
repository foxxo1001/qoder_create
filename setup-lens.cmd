@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\setup-lens.ps1" -Root "%~dp0"
pause