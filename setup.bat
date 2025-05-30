@echo off
echo Setting up VoicePractice environment...

:: Step 0: Check if venv exists
if exist "venv\Scripts\python.exe" (
    echo Virtual environment already exists.
    goto :activate_venv
)

:: Step 1: Create virtual environment
python -m venv venv
if %ERRORLEVEL% NEQ 0 (
    echo Failed to create virtual environment. Make sure Python is installed and in PATH.
    exit /b 1
)
echo Virtual environment created.

:activate_venv
:: Step 2: Activate the virtual environment
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo Failed to activate virtual environment.
    exit /b 1
)
echo Virtual environment activated.

:: Step 3: Ensure pip is available
python -m ensurepip

:: Step 4: Install dependencies
if not exist requirements.txt (
    echo requirements.txt not found.
    exit /b 1
)
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Failed to install requirements.
    exit /b 1
)
echo Dependencies installed.

:: Step 5: Run the CLI tester
echo Starting CLI pitch tester...
python test_pitch_cli.py
