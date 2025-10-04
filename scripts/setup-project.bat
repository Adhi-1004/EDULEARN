@echo off
echo ========================================
echo modLRN Project Setup
echo ========================================
echo.

echo Checking system requirements...

echo.
echo Checking Python...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo.
echo Checking Node.js...
node --version
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed
    echo Please install Node.js 18+ from https://nodejs.org
    pause
    exit /b 1
)

echo.
echo Setting up backend...
cd /d "%~dp0\..\backend"

echo Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Python dependencies
    pause
    exit /b 1
)

echo.
echo Setting up frontend...
cd /d "%~dp0\..\frontend"

echo Installing Node.js dependencies...
npm install
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Node.js dependencies
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup completed successfully!
echo.
echo Next steps:
echo 1. Copy env.example to backend/.env and configure your settings
echo 2. Start MongoDB service
echo 3. Run start-full-stack.bat to start both servers
echo ========================================
pause
