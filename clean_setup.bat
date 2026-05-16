@echo off
echo --- InstaViral: Clean Setup ---
echo WARNING: This will delete your current virtual environment and reinstall everything.
pause

if exist venv (
    echo Deleting existing venv...
    rmdir /s /q venv
)

echo Starting fresh setup...
call setup.bat
