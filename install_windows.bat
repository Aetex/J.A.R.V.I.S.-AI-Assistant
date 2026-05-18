@echo off
title J.A.R.V.I.S. Installer
echo ===================================================
echo   J.A.R.V.I.S. AUTOMATED INSTALLATION (WINDOWS)
echo ===================================================
echo.

:: Get the current directory
set "BASE_DIR=%~dp0"
cd /d "%BASE_DIR%"

echo [*] Step 1: Creating Python Virtual Environment...
if not exist "venv" (
    python -m venv venv
    echo [OK] Virtual environment created.
) else (
    echo [OK] Virtual environment already exists.
)
echo.

echo [*] Step 2: Installing Python Core Dependencies...
call "%BASE_DIR%venv\Scripts\activate.bat"
python -m pip install --upgrade pip > nul
pip install -r requirements.txt
echo [OK] Python dependencies installed.
echo.

echo [*] Step 3: Installing UI Components...
cd ui
call npm install
cd ..
echo [OK] UI components installed.
echo.

echo ===================================================
echo   INSTALLATION COMPLETE!
echo ===================================================
echo.
echo Please complete the final step manually:
echo 1. Rename .env.example to .env
echo 2. Open it and paste your API key inside.
echo.
echo Once done, you can launch the system using:
echo launch_jarvis.bat
echo.
pause
