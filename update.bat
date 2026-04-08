@echo off
title Queens Cafe POS - Update
color 0A
echo.
echo ============================================================
echo   QUEENS CAFE POS - UPDATE
echo   Applying latest updates...
echo ============================================================
echo.

set INSTALL_DIR=%USERPROFILE%\Desktop\CAFE
set STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup

if not exist "%INSTALL_DIR%" (
    echo [ERROR] CAFE POS not found on Desktop. Run the full installer first.
    pause & exit /b 1
)

echo [1/4] Copying updated files...
xcopy /y /q "%~dp0web.py" "%INSTALL_DIR%\"
xcopy /y /q "%~dp0database.py" "%INSTALL_DIR%\"
xcopy /y /q "%~dp0printer.py" "%INSTALL_DIR%\"
xcopy /y /q "%~dp0autostart.vbs" "%INSTALL_DIR%\"
xcopy /y /q "%~dp0templates\*" "%INSTALL_DIR%\templates\"
echo      Files copied OK.
echo.

echo [2/4] Fixing cafe name...
python -c "import sqlite3; conn=sqlite3.connect('%INSTALL_DIR%\cafe_pos.db'); conn.execute(\"UPDATE settings SET value='QUEENS CAFE HOTEL' WHERE key='cafe_name'\"); conn.commit(); conn.close(); print('     Cafe name updated OK.')"
echo.

echo [3/4] Installing auto-start on Windows login...
copy /y "%INSTALL_DIR%\autostart.vbs" "%STARTUP_DIR%\QueensCafePOS.vbs" >nul
echo      Auto-start installed OK.
echo      (Server + browser will open automatically when this PC turns on)
echo.

echo [4/4] Done!
echo.
echo ============================================================
echo   UPDATE COMPLETE!
echo   Please restart the POS system:
echo   1. Close the black command window
echo   2. Double-click "Queens Cafe POS" on the Desktop
echo   3. From next startup, it will launch automatically!
echo ============================================================
echo.
pause
