@echo off
title J.A.R.V.I.S. Installer
echo ===================================================
echo   J.A.R.V.I.S. AUTOMATED INSTALLATION (WINDOWS)
echo ===================================================
echo.

:: Get the current directory
set "BASE_DIR=%~dp0"
cd /d "%BASE_DIR%"

goto after_jokes

:joke_python
echo         JARVIS: I appear to be missing a brain, sir. Python would be a fine place to start.
exit /b 0

:joke_node
echo         Tony Stark: No Node? That's not a setup, that's a cry for an upgrade.
exit /b 0

:joke_pip
echo         Tony Stark: Dependency chaos. Classic. I usually fix this with a suit and questionable confidence.
exit /b 0

:joke_ui
echo         JARVIS: The HUD refuses to assemble. Even Stark tech needs its npm bolts tightened.
exit /b 0

:run_spinner
set "SPIN_MSG=%~1"
set "SPIN_CMD=%~2"
set "SPIN_LOG=%TEMP%\jarvis-install-%RANDOM%.log"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$msg=$env:SPIN_MSG; $cmd=$env:SPIN_CMD + ' > \"' + $env:SPIN_LOG + '\" 2>&1'; $log=$env:SPIN_LOG; $p=Start-Process -FilePath 'cmd.exe' -ArgumentList '/d','/s','/c',$cmd -WindowStyle Hidden -PassThru; $spin='|','/','-','\'; $i=0; while(-not $p.HasExited){ Write-Host -NoNewline (\"`r[*] {0} {1}\" -f $msg,$spin[$i%%4]); Start-Sleep -Milliseconds 120; $i++ }; $p.WaitForExit(); Write-Host -NoNewline \"`r\"; if($p.ExitCode -ne 0){ $saved=Join-Path (Get-Location) 'jarvis-install-error.log'; if(Test-Path $log){ Move-Item -Force $log $saved }; Write-Host \"[ERROR] $msg failed.\"; if((Test-Path $saved) -and (Select-String -Path $saved -Pattern 'Failed to resolve|NameResolutionError|Temporary failure|Could not resolve|unreachable network|WinError 10051' -Quiet)){ Write-Host '        Network connection failed. Check your internet/DNS, then re-run this installer.' } else { Write-Host \"        Full technical details were saved to $saved\" }; exit $p.ExitCode }; if(Test-Path $log){ Remove-Item $log -ErrorAction SilentlyContinue }; Write-Host \"[OK] $msg complete.\"; exit 0"
exit /b %errorlevel%

:after_jokes
echo [*] Pre-flight: Checking Python...
where python > nul 2>&1
if %errorlevel% neq 0 (
    echo ===================================================
    echo   J.A.R.V.I.S. SYSTEM ALERT
    echo ===================================================
    echo [ERROR] Python is not installed or not available on PATH.
    call :joke_python
    echo         Arc reactor offline. Please install Python from:
    echo         https://www.python.org/downloads/windows/
    echo.
    echo         During setup, enable "Add python.exe to PATH".
    echo         Then re-run this installer.
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
    call :run_spinner "Installing Node.js LTS" "winget install --id OpenJS.NodeJS.LTS -e --accept-package-agreements --accept-source-agreements"
    if %errorlevel% neq 0 goto node_install_failed
    goto refresh_node_path
)

where choco > nul 2>&1
if %errorlevel% equ 0 (
    call :run_spinner "Installing Node.js LTS" "choco install nodejs-lts -y"
    if %errorlevel% neq 0 goto node_install_failed
    goto refresh_node_path
)

echo [ERROR] Could not find winget or Chocolatey to install Node.js automatically.
call :joke_node
echo         Install Node.js LTS from https://nodejs.org/ and re-run this installer.
pause
exit /b 1

:node_install_failed
echo [ERROR] Node.js installation failed.
call :joke_node
echo         Install Node.js LTS from https://nodejs.org/ and re-run this installer.
pause
exit /b 1

:refresh_node_path
set "PATH=%ProgramFiles%\nodejs;%AppData%\npm;%PATH%"
where node > nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js was installed, but it is not available in this terminal yet.
    call :joke_node
    echo         Close this window, open a new terminal, and re-run this installer.
    pause
    exit /b 1
)
where npm > nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] npm was installed, but it is not available in this terminal yet.
    call :joke_node
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
call :run_spinner "Upgrading pip" "python -m pip install --upgrade pip"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to upgrade pip.
    call :joke_pip
    pause
    exit /b 1
)
call :run_spinner "Installing Python dependencies" "pip install --progress-bar off -r requirements.txt"
if %errorlevel% neq 0 (
    echo [ERROR] Python dependency installation failed.
    call :joke_pip
    pause
    exit /b 1
)
echo [OK] Python dependencies installed.
echo.

echo [*] Step 4: Installing UI Components...
cd ui
call :run_spinner "Installing UI components" "npm install --silent"
if %errorlevel% neq 0 (
    echo [ERROR] UI dependency installation failed.
    call :joke_ui
    pause
    exit /b 1
)
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
