@echo off
title Queens Cafe POS
cd /d "%~dp0"

:: Suppress Python path warnings on older Windows
set PYTHONWARNINGS=ignore

:: Start the POS kiosk (no console window)
start "" pythonw app.py

:: If pythonw fails, fall back to python
if errorlevel 1 (
    python app.py
)
