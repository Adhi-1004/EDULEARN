@echo off
echo Starting modLRN Backend Server with RBAC...
echo ==========================================

cd backend

echo Starting FastAPI server on port 5001...
echo Server will be available at: http://127.0.0.1:5001
echo API documentation: http://127.0.0.1:5001/docs
echo ==========================================

python -m uvicorn app.main:app --host 127.0.0.1 --port 5001 --reload

pause
