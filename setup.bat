@echo off
echo === Personal Assistant Setup ===
echo This script will help you set up the Personal Assistant.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is required but not installed.
    echo Please install Python and try again.
    exit /b 1
)

REM Create virtual environment
echo.
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt

REM Create necessary directories
echo.
echo Creating necessary directories...
if not exist data mkdir data
if not exist credentials mkdir credentials

REM Check for OpenAI API key
if exist .env (
    echo.
    echo Found .env file.
) else (
    echo.
    echo Creating .env file...
    set /p api_key="Please enter your OpenAI API key: "
    echo OPENAI_API_KEY=%api_key%> .env
    echo Created .env file with API key.
)

echo.
echo === Setup Complete ===
echo To start using the Personal Assistant:
echo 1. Activate the virtual environment:
echo    venv\Scripts\activate
echo 2. Run the assistant:
echo    python run.py --mode basic
echo.
echo For more information, see the README.md and INTEGRATIONS.md files.

pause 