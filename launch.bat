@echo off
title PEconomy
cd /d "%~dp0"

echo.
echo  Starting PEconomy...
echo.

:: Start Streamlit headless (no auto browser open)
start /B "" streamlit run bin\main.py --server.headless true --server.port 8501

:: Wait for server to be ready
timeout /t 3 /nobreak > nul

:: Find Chrome path via Windows registry
for /f "tokens=2*" %%a in ('reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe" /ve 2^>nul') do set CHROME=%%b
if not defined CHROME (
    for /f "tokens=2*" %%a in ('reg query "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe" /ve 2^>nul') do set CHROME=%%b
)

if defined CHROME (
    :: --user-data-dir forces a new Chrome instance independent of any open windows
    :: Without it, Chrome reuses the existing process and ignores --app, opening a tab instead
    start "" "%CHROME%" --app=http://localhost:8501 --user-data-dir="%APPDATA%\PEconomy-App" --no-first-run --window-size=1440,900 --window-position=40,40
) else (
    echo Chrome not found - opening in default browser...
    start http://localhost:8501
)
