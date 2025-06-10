@echo off
echo Fontshare Bulk Font Downloader
echo ===============================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Check if requirements are installed
echo Checking dependencies...
pip show aiohttp >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo Starting font download...
echo You can press Ctrl+C to stop the download at any time.
echo.

REM Run the downloader
python fontshare_downloader.py

echo.
echo Download process completed!
pause
