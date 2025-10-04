@echo off
echo Starting modLRN Backend Server...
echo ====================================

cd backend

echo Starting FastAPI server on port 5001...
python -m uvicorn app.main:app --host 127.0.0.1 --port 5001 --reload

pause
