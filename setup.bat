@echo off
title Queens Cafe POS - Setup
color 0A
echo ============================================================
echo   QUEENS CAFE POS - Setup for Windows 10
echo   Target: Windows 10 Pro (Build 14393+), 2GB RAM
echo ============================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo.
    echo Please install Python 3.11 manually:
    echo   1. Go to: https://www.python.org/downloads/release/python-3119/
    echo   2. Download "Windows installer (64-bit)"
    echo   3. Run installer and CHECK "Add Python to PATH"
    echo   4. Re-run this setup.bat
    echo.
    pause
    exit /b 1
)

echo [OK] Python found:
python --version
echo.

:: Check Python version is 3.8 or higher
python -c "import sys; exit(0 if sys.version_info >= (3,8) else 1)"
if errorlevel 1 (
    echo [ERROR] Python 3.8 or higher is required.
    echo         Please install Python 3.11 from python.org
    pause
    exit /b 1
)

echo [INFO] Installing required packages...
echo.
pip install --upgrade pip --quiet
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [ERROR] Package installation failed.
    echo         Check your internet connection and try again.
    pause
    exit /b 1
)

echo.
echo [INFO] Optional: Install pywin32 for USB printer support
set /p INSTALL_WIN32="Install pywin32 for USB printing? (y/n): "
if /i "%INSTALL_WIN32%"=="y" (
    pip install pywin32==306
    python -m pywin32_postinstall -install 2>nul
)

echo.
echo ============================================================
echo   Setup complete!
echo   Run start_pos.bat to launch the POS system.
echo   Run start_web.bat to launch the web dashboard.
echo ============================================================
echo.
pause
