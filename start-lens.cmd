@echo off
setlocal
cd /d "%~dp0"
where curl.exe >nul 2>nul
if errorlevel 1 goto nocurl

curl.exe -s -o NUL --max-time 1 "http://127.0.0.1:8765/health" >nul 2>nul
if not errorlevel 1 goto open

where pythonw.exe >nul 2>nul
if errorlevel 1 goto nopy

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\start-bridge.ps1"

for /l %%i in (1,1,25) do (
  %SystemRoot%\System32\ping.exe -n 2 127.0.0.1 >nul
  curl.exe -s -o NUL --max-time 1 "http://127.0.0.1:8765/health" >nul 2>nul
  if not errorlevel 1 goto open
)

echo EmbeddedLens bridge did not start.
echo Check tools\bridge.log for details.
pause
exit /b 1

:open
if /i "%ELENS_NO_OPEN%"=="1" (
  echo EmbeddedLens bridge is ready at http://127.0.0.1:8765/
  exit /b 0
)
start "" "http://127.0.0.1:8765/"
exit /b 0

:nopy
echo pythonw.exe not found. Install Python and add it to PATH.
pause
exit /b 1

:nocurl
echo curl.exe not found. Windows 10 or later is required.
pause
exit /b 1