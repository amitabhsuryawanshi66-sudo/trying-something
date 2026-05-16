@echo off
setlocal enabledelayedexpansion

echo --- InstaViral: Robust Windows Setup ---
echo.

:: 1. Detect Python
set PYTHON_EXE=python
where py >nul 2>nul
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('py -3.11 -c "import sys; print(sys.executable)" 2^>nul') do set PYTHON_EXE=%%i
)

:: 2. Check Python Version
echo Checking Python version...
%PYTHON_EXE% -c "import sys; v=sys.version_info; sys.exit(0 if v.major==3 and v.minor in [10,11,12] else 1)"
if %errorlevel% neq 0 (
    echo [ERROR] Unsupported Python version.
    %PYTHON_EXE% --version
    echo Please install Python 3.11 from https://www.python.org/
    echo During installation, make sure to check "Add Python to PATH".
    pause
    exit /b 1
)
%PYTHON_EXE% --version

:: 3. Check SSL
echo Checking SSL module...
%PYTHON_EXE% -c "import ssl; print('SSL OK:', ssl.OPENSSL_VERSION)"
if %errorlevel% neq 0 (
    echo [ERROR] Your Python SSL module is broken or outdated.
    echo This usually happens with unofficial or incomplete Python installs.
    echo Please reinstall official Python 3.11 from https://www.python.org/
    pause
    exit /b 1
)

:: 4. Create/Activate Venv
if not exist venv (
    echo Creating virtual environment...
    %PYTHON_EXE% -m venv venv
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b !errorlevel!
    )
)

echo Activating virtual environment...
call venv\Scripts\activate
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b %errorlevel%
)

:: 5. Upgrade Base Tools
echo Upgrading pip, setuptools, and wheel...
python -m pip install --upgrade pip setuptools wheel
if %errorlevel% neq 0 (
    echo [ERROR] Failed to upgrade base tools.
    goto :FAIL
)

:: 6. Install Binary Wheels First (Critical for Windows)
echo Installing critical binary wheels...
python -m pip install --only-binary=:all: "tornado>=6.3.3,<7" Pillow
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install binary wheels.
    goto :FAIL
)

:: 7. Install Full Requirements
echo Installing all requirements...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install requirements.
    goto :FAIL
)

:: 8. Config
if not exist .env (
    echo Creating .env file...
    copy .env.example .env
)

echo.
echo --- Setup Successful! ---
echo.
echo You can now start the app by double-clicking run_app.bat
echo.
pause
exit /b 0

:FAIL
echo.
echo [ERROR] Setup failed.
echo If you see 'tornado' or 'build' errors, try running clean_setup.bat
echo or reinstalling Python 3.11 (Official).
echo.
pause
exit /b 1
