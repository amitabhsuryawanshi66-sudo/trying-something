@echo off
echo --- Instagram Reel Automator Setup ---
echo.
echo IMPORTANT: For automated viral captions, you MUST install ImageMagick.
echo Download it from: https://imagemagick.org/script/download.php
echo (Check "Install legacy utilities (e.g. convert)" during installation).
echo.
echo Creating virtual environment...
python -m venv venv
echo Activating virtual environment and installing requirements...
call venv\Scripts\activate
pip install -r requirements.txt
if not exist .env (
    echo Creating .env file from .env.example...
    copy .env.example .env
    echo PLEASE EDIT .env AND ADD YOUR OPENAI_API_KEY
)
echo --- Setup Complete! ---
pause
