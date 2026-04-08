@echo off
setlocal
title VocalFlow Windows — Setup
color 0A

echo.
echo  =========================================================
echo   VocalFlow Windows  —  Setup
echo  =========================================================
echo.

:: ── Step 1: Find Python ─────────────────────────────────────
echo  [Step 1] Checking Python...
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  ERROR: Python is not found.
    echo.
    echo  Please install Python from:
    echo  https://www.python.org/downloads/
    echo.
    echo  During install, CHECK the box: "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

python --version
echo  Python found OK.
echo.

:: ── Step 2: Upgrade pip ──────────────────────────────────────
echo  [Step 2] Upgrading pip...
python -m pip install --upgrade pip --quiet
echo  pip OK.
echo.

:: ── Step 3: Install packages ─────────────────────────────────
echo  [Step 3] Installing packages...
echo  (This may take 1-2 minutes, please wait)
echo.

echo  Installing numpy (latest - supports Python 3.14)...
python -m pip install "numpy>=2.0" --quiet
if %errorlevel% neq 0 ( echo  FAILED: numpy & goto :error )
echo  OK: numpy

echo  Installing sounddevice...
python -m pip install sounddevice --quiet
if %errorlevel% neq 0 ( echo  FAILED: sounddevice & goto :error )
echo  OK: sounddevice

echo  Installing requests...
python -m pip install requests --quiet
if %errorlevel% neq 0 ( echo  FAILED: requests & goto :error )
echo  OK: requests

echo  Installing Pillow...
python -m pip install Pillow --quiet
if %errorlevel% neq 0 ( echo  FAILED: Pillow & goto :error )
echo  OK: Pillow

echo  Installing pystray...
python -m pip install pystray --quiet
if %errorlevel% neq 0 ( echo  FAILED: pystray & goto :error )
echo  OK: pystray

echo  Installing keyboard...
python -m pip install keyboard --quiet
if %errorlevel% neq 0 ( echo  FAILED: keyboard & goto :error )
echo  OK: keyboard

echo  Installing pyperclip...
python -m pip install pyperclip --quiet
if %errorlevel% neq 0 ( echo  FAILED: pyperclip & goto :error )
echo  OK: pyperclip

echo  Installing pyautogui...
python -m pip install pyautogui --quiet
if %errorlevel% neq 0 ( echo  FAILED: pyautogui & goto :error )
echo  OK: pyautogui

echo.
echo  =========================================================
echo   ALL DONE! Setup complete.
echo  =========================================================
echo.
echo   Next steps:
echo   1. Right-click config.py ^> Open with ^> Notepad
echo      Add your Deepgram and Groq API keys
echo   2. Right-click run.bat ^> Run as administrator
echo  =========================================================
echo.
pause
exit /b 0

:error
echo.
echo  =========================================================
echo   INSTALLATION FAILED - Read below for fix
echo  =========================================================
echo.
echo  Your Python version is likely 3.14 (very new).
echo  Try running these commands manually:
echo.
echo  Open Command Prompt as Admin, then type:
echo.
echo    python -m pip install "numpy>=2.0"
echo    python -m pip install sounddevice requests
echo    python -m pip install Pillow pystray keyboard
echo    python -m pip install pyperclip pyautogui
echo.
pause
exit /b 1
