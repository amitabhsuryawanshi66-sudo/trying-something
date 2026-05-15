@echo off
setlocal enabledelayedexpansion

echo --- Instagram Reel Automator Setup ---
echo.
echo IMPORTANT: For automated viral captions, you MUST install ImageMagick.
echo Download it from: https://imagemagick.org/script/download.php
echo (Check "Install legacy utilities (e.g. convert)" during installation).
echo.

echo Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create virtual environment.
    pause
    exit /b %errorlevel%
)

echo Activating virtual environment...
call venv\Scripts\activate
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b %errorlevel%
)

echo Upgrading basic tools...
python -m pip install --upgrade pip setuptools wheel
if %errorlevel% neq 0 (
    echo [ERROR] Failed to upgrade pip/setuptools.
    pause
    exit /b %errorlevel%
)

echo Installing prebuilt Pillow binary...
python -m pip install --only-binary=:all: Pillow
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Pillow.
    pause
    exit /b %errorlevel%
)

echo Installing all requirements...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install requirements.
    pause
    exit /b %errorlevel%
)

if not exist .env (
    echo Creating .env file from .env.example...
    copy .env.example .env
    echo PLEASE EDIT .env AND ADD YOUR API KEYS
)

echo.
echo --- Setup Successful! ---
echo.
echo You can now start the app by double-clicking run_app.bat
echo.
pause
