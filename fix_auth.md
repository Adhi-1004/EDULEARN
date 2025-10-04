# Fix Authentication Issues

## Problem
The login and signup functionality is not working properly after adding AI features to the dashboards.

## Solution

### 1. Start the Backend Server
Run the following command to start the backend server:

```bash
# Option 1: Use the batch file
start_server.bat

# Option 2: Use the Python script
python start_backend.py

# Option 3: Manual start
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 5001 --reload
```

### 2. Test Authentication
Run the test script to verify authentication is working:

```bash
python test_login.py
```

### 3. Start the Frontend
In a separate terminal, start the frontend:

```bash
cd frontend
npm run dev
```

## Troubleshooting

### If the server won't start:
1. Check if port 5001 is already in use
2. Make sure MongoDB is running
3. Check the console for error messages

### If authentication fails:
1. Check the browser console for errors
2. Verify the API base URL in `frontend/src/utils/api.ts`
3. Make sure the backend is running on port 5001

### If you get CORS errors:
1. Check the CORS settings in `backend/app/main.py`
2. Make sure the frontend is running on port 5173

## Expected Behavior

1. **Login**: Should redirect to appropriate dashboard based on role
   - Student → `/dashboard`
   - Teacher → `/teacher-dashboard`
   - Admin → `/admin-dashboard`

2. **Signup**: Should create new user and redirect to dashboard

3. **Authentication**: Should persist across page refreshes

## Files Modified

- `backend/app/main.py` - Fixed merge conflicts and imports
- `backend/app/api/__init__.py` - Added enhanced routers
- `backend/app/api/enhanced_*.py` - Fixed import paths
- `start_backend.py` - Fixed server startup configuration
- `start_server.bat` - Created batch file for easy server startup

## Verification

The authentication system has been tested and is working correctly. The issue was with the server startup configuration, which has been fixed.
