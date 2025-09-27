@echo off
echo Starting modLRN Backend Server...
echo.

cd backend

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing/updating dependencies...
pip install -r requirements.txt

echo.
echo Starting FastAPI server on http://localhost:5001
echo Press Ctrl+C to stop the server
echo.

python main.py
