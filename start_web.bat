@echo off
title Queens Cafe POS - Web Dashboard
cd /d "%~dp0"
echo ============================================================
echo   QUEENS CAFE - Web Dashboard
echo   Open browser: http://localhost:5000
echo   Login: admin / admin123
echo   Press Ctrl+C to stop.
echo ============================================================
echo.
set PYTHONWARNINGS=ignore
python web.py
pause
