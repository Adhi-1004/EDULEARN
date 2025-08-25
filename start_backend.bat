@echo off
echo Starting EduLearn AI Backend Server...
echo.
echo Make sure you have Python installed and dependencies installed:
echo pip install -r Backend/requirements.txt
echo.
cd Backend
echo Starting server on http://localhost:5003
echo Press Ctrl+C to stop the server
echo.
python app.py
pause
