@echo off
setlocal
title VocalFlow Windows

:: ── Request admin (required by keyboard library) ────────────────────
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo  Requesting administrator privileges...
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

:: ── Launch ──────────────────────────────────────────────────────────
cd /d "%~dp0"
echo.
echo  Starting VocalFlow...
echo  Look for the microphone icon in your system tray (bottom-right).
echo  Right-click the tray icon for Settings and API Balances.
echo.

python main.py

if %errorlevel% neq 0 (
    echo.
    echo  [ERROR] VocalFlow exited with an error.
    echo  Make sure you have run setup.bat first.
    echo.
    pause
)
