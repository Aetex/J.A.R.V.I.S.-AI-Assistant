@echo off
title J.A.R.V.I.S. Installer
echo ===================================================
echo   J.A.R.V.I.S. AUTOMATED INSTALLATION (WINDOWS)
echo ===================================================
echo.

:: Get the current directory
set "BASE_DIR=%~dp0"
cd /d "%BASE_DIR%"

echo [*] Pre-flight: Checking Python...
where python > nul 2>&1
if %errorlevel% neq 0 (
    echo ===================================================
    echo   J.A.R.V.I.S. SYSTEM ALERT
    echo ===================================================
    echo [ERROR] Python is not installed or not available on PATH.
    echo         Arc reactor offline. Install Python, then re-run this installer.
    echo ===================================================
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo [OK] Python detected: %%v
echo.

echo [*] Step 1: Checking Node.js and npm...
where node > nul 2>&1
if %errorlevel% neq 0 (
    goto install_node
)
where npm > nul 2>&1
if %errorlevel% neq 0 (
    goto install_node
)
echo [OK] Node.js and npm are already installed.
goto node_done

:install_node
echo [*] Installing Node.js LTS...
where winget > nul 2>&1
if %errorlevel% equ 0 (
    winget install --id OpenJS.NodeJS.LTS -e --accept-package-agreements --accept-source-agreements
    if %errorlevel% neq 0 goto node_install_failed
    goto refresh_node_path
)

where choco > nul 2>&1
if %errorlevel% equ 0 (
    choco install nodejs-lts -y
    if %errorlevel% neq 0 goto node_install_failed
    goto refresh_node_path
)

echo [ERROR] Could not find winget or Chocolatey to install Node.js automatically.
echo         Install Node.js LTS from https://nodejs.org/ and re-run this installer.
pause
exit /b 1

:node_install_failed
echo [ERROR] Node.js installation failed.
echo         Install Node.js LTS from https://nodejs.org/ and re-run this installer.
pause
exit /b 1

:refresh_node_path
set "PATH=%ProgramFiles%\nodejs;%AppData%\npm;%PATH%"
where node > nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js was installed, but it is not available in this terminal yet.
    echo         Close this window, open a new terminal, and re-run this installer.
    pause
    exit /b 1
)
where npm > nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] npm was installed, but it is not available in this terminal yet.
    echo         Close this window, open a new terminal, and re-run this installer.
    pause
    exit /b 1
)
echo [OK] Node.js and npm installed.

:node_done
echo.

echo [*] Step 2: Creating Python Virtual Environment...
if not exist "venv" (
    python -m venv venv
    echo [OK] Virtual environment created.
) else (
    echo [OK] Virtual environment already exists.
)
echo.

echo [*] Step 3: Installing Python Core Dependencies...
call "%BASE_DIR%venv\Scripts\activate.bat"
python -m pip install --upgrade pip > nul
pip install -r requirements.txt
echo [OK] Python dependencies installed.
echo.

echo [*] Step 4: Installing UI Components...
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
