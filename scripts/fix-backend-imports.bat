@echo off
echo ========================================
echo Fixing Backend Import Issues
echo ========================================
echo.

cd /d "%~dp0\..\backend"

echo The correct way to run the backend is:
echo.
echo 1. From the backend directory:
echo    cd backend
echo.
echo 2. Activate virtual environment:
echo    venv\Scripts\activate
echo.
echo 3. Run with uvicorn (NOT python main.py):
echo    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 5001
echo.
echo OR use the startup script:
echo    scripts\start-backend.bat
echo.
echo ========================================
echo.
echo Press any key to run the correct command...
pause

echo.
echo Running the correct command now...
call venv\Scripts\activate.bat
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 5001
