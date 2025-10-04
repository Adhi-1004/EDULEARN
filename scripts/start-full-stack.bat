@echo off
echo ========================================
echo Starting modLRN Full Stack Application
echo ========================================
echo.

echo Starting backend server in new window...
start "modLRN Backend" cmd /k "cd /d \"%~dp0\..\backend\" && call venv\Scripts\activate.bat && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 5001"

echo Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo.
echo Starting frontend server in new window...
start "modLRN Frontend" cmd /k "cd /d \"%~dp0\..\frontend\" && npm run dev"

echo.
echo ========================================
echo Both servers are starting...
echo.
echo Backend:  http://localhost:5001
echo Frontend: http://localhost:5173
echo.
echo API Documentation: http://localhost:5001/docs
echo ========================================
echo.
echo Press any key to exit this launcher...
pause > nul
