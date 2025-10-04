@echo off
echo ========================================
echo Starting modLRN Backend Server
echo ========================================
echo.

cd /d "%~dp0\..\backend"

echo Checking Python environment...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo.
echo Checking virtual environment...
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Starting FastAPI server...
echo Server will be available at: http://localhost:5001
echo API documentation: http://localhost:5001/docs
echo.
echo Press Ctrl+C to stop the server
echo ========================================

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 5001

pause