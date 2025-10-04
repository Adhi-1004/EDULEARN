# 🔧 Fix Login Issue - Step by Step

## Problem:
- Frontend shows 500 Internal Server Error when trying to login
- Backend server may not be running properly

## Solution:

### Step 1: Stop All Running Servers
```cmd
# Kill all Python processes
taskkill /f /im python.exe
taskkill /f /im uvicorn.exe
```

### Step 2: Start Backend Server
```cmd
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 5001 --reload
```

### Step 3: Start Frontend Server (in new terminal)
```cmd
cd frontend
npm run dev
```

### Step 4: Test Login
Use these credentials:
- **Email:** `adhithya.admin@modlrn.com`
- **Password:** `admin123`

## Alternative Working Credentials:
- **Email:** `admin@modlrn.com`
- **Password:** `admin123`

## Quick Fix Script:
Run this PowerShell script to restart everything:

```powershell
# Kill existing processes
Get-Process | Where-Object {$_.ProcessName -like "*python*" -or $_.ProcessName -like "*node*"} | Stop-Process -Force

# Start backend
Start-Process -FilePath "cmd" -ArgumentList "/c", "cd backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 5001 --reload" -WindowStyle Minimized

# Start frontend  
Start-Process -FilePath "cmd" -ArgumentList "/c", "cd frontend && npm run dev" -WindowStyle Minimized

Write-Host "Servers starting... Wait 10 seconds then go to http://localhost:5173"
```

## Verification:
1. Go to http://localhost:5173
2. Click Login
3. Enter: `adhithya.admin@modlrn.com` / `admin123`
4. Should login successfully to admin dashboard
