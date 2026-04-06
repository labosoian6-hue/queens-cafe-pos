@echo off
title Queens Cafe POS - Auto Installer
color 0A
echo.
echo ============================================================
echo   QUEENS CAFE POS - AUTO INSTALLER
echo   This will set up everything automatically.
echo ============================================================
echo.

set INSTALL_DIR=%USERPROFILE%\Desktop\CAFE
set REPO_URL=https://github.com/labosoian6-hue/queens-cafe-pos.git
set PYTHON_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
set PYTHON_INSTALLER=%TEMP%\python-3.11.9-amd64.exe

:: ── STEP 1: Check Python ──────────────────────────────────────────────────
echo [1/5] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo      Python not found. Downloading Python 3.11...
    powershell -Command "Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_INSTALLER%' -UseBasicParsing"
    if errorlevel 1 (
        echo [ERROR] Could not download Python. Check internet connection.
        pause & exit /b 1
    )
    echo      Installing Python 3.11 silently...
    "%PYTHON_INSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_launcher=1
    if errorlevel 1 (
        echo [ERROR] Python installation failed.
        pause & exit /b 1
    )
    :: Refresh PATH
    call refreshenv >nul 2>&1
    set "PATH=%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts;%PATH%"
    echo      Python 3.11 installed OK.
) else (
    echo      Python already installed:
    python --version
)
echo.

:: ── STEP 2: Check Git ────────────────────────────────────────────────────
echo [2/5] Checking Git...
git --version >nul 2>&1
if errorlevel 1 (
    echo      Git not found. Downloading via PowerShell...
    powershell -Command "& {$r='https://github.com/git-for-windows/git/releases/download/v2.45.2.windows.1/Git-2.45.2-64-bit.exe'; $o='%TEMP%\git-installer.exe'; Invoke-WebRequest $r -OutFile $o -UseBasicParsing; Start-Process $o '/VERYSILENT /NORESTART' -Wait}"
    set "PATH=C:\Program Files\Git\cmd;%PATH%"
    echo      Git installed OK.
) else (
    echo      Git already installed.
)
echo.

:: ── STEP 3: Clone / Update repo ──────────────────────────────────────────
echo [3/5] Getting latest CAFE POS from GitHub...
if exist "%INSTALL_DIR%\.git" (
    echo      Updating existing installation...
    cd /d "%INSTALL_DIR%"
    git pull
) else (
    if exist "%INSTALL_DIR%" rd /s /q "%INSTALL_DIR%"
    git clone "%REPO_URL%" "%INSTALL_DIR%"
    if errorlevel 1 (
        echo [ERROR] Could not download from GitHub. Check internet connection.
        pause & exit /b 1
    )
)
echo.

:: ── STEP 4: Install Python packages ──────────────────────────────────────
echo [4/5] Installing Python packages...
cd /d "%INSTALL_DIR%"
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERROR] Package installation failed.
    pause & exit /b 1
)
echo      Packages installed OK.
echo.

:: ── STEP 5: Create Desktop shortcut ──────────────────────────────────────
echo [5/5] Creating Desktop shortcut...
set SHORTCUT=%USERPROFILE%\Desktop\Queens Cafe POS.lnk
powershell -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%SHORTCUT%'); $s.TargetPath='%INSTALL_DIR%\start_pos.bat'; $s.WorkingDirectory='%INSTALL_DIR%'; $s.IconLocation='%SystemRoot%\System32\shell32.dll,137'; $s.Save()"
echo      Shortcut created on Desktop.
echo.

echo ============================================================
echo   INSTALLATION COMPLETE!
echo.
echo   Double-click "Queens Cafe POS" on the Desktop to start.
echo   OR run: start_pos.bat
echo.
echo   Web dashboard: run start_web.bat
echo   then open browser to http://localhost:5000
echo ============================================================
echo.
pause
