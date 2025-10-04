@echo off
echo ========================================
echo Starting modLRN Frontend Server
echo ========================================
echo.

cd /d "%~dp0\..\frontend"

echo Checking Node.js environment...
node --version
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 18+ and try again
    pause
    exit /b 1
)

echo.
echo Checking npm...
npm --version
if %errorlevel% neq 0 (
    echo ERROR: npm is not available
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
npm install
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Starting development server...
echo Frontend will be available at: http://localhost:5173
echo.
echo Press Ctrl+C to stop the server
echo ========================================

npm run dev

pause