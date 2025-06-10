@echo off
echo.
echo ==========================================
echo    Font Installation Troubleshooter
echo ==========================================
echo.
echo This will clean existing fonts and install
echo a few test fonts to diagnose the issue.
echo.

:: Check for admin privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Running as Administrator
    echo.
) else (
    echo ❌ This script must be run as Administrator!
    echo.
    echo Please right-click this file and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo Running font troubleshooter...
echo.

python font_troubleshooter.py

echo.
echo Troubleshooting completed!
echo.
pause
