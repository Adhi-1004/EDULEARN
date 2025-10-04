# modLRN Troubleshooting Guide

## 🚨 Common Issues and Solutions

### 1. Backend Import Errors

**Problem**: `ImportError: attempted relative import with no known parent package`

**Cause**: Trying to run `python main.py` directly from the `app` directory.

**Solution**:
```bash
# WRONG - Don't do this:
cd backend\app
python main.py

# CORRECT - Do this instead:
cd backend
venv\Scripts\activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 5001

# OR use the startup script:
scripts\start-backend.bat
```

### 2. Python Not Found

**Problem**: `'python' is not recognized as an internal or external command`

**Solution**:
1. Install Python 3.8+ from [python.org](https://python.org)
2. Make sure to check "Add Python to PATH" during installation
3. Restart your terminal/command prompt
4. Verify with: `python --version`

### 3. Node.js Not Found

**Problem**: `'node' is not recognized as an internal or external command`

**Solution**:
1. Install Node.js 18+ from [nodejs.org](https://nodejs.org)
2. Restart your terminal/command prompt
3. Verify with: `node --version`

### 4. MongoDB Connection Failed

**Problem**: Database connection errors in backend logs

**Solution**:
1. Install MongoDB from [mongodb.com](https://mongodb.com)
2. Start MongoDB service:
   ```bash
   # Windows
   net start MongoDB
   
   # Or start manually
   mongod
   ```
3. Check if MongoDB is running on port 27017
4. Verify connection in your `.env` file:
   ```env
   MONGO_URI=mongodb://localhost:27017
   ```

### 5. Port Already in Use

**Problem**: `Address already in use` or `Port 5001/5173 is already in use`

**Solution**:
```bash
# Find and kill processes using the ports
netstat -ano | findstr :5001
netstat -ano | findstr :5173

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or restart your computer
```

### 6. Virtual Environment Issues

**Problem**: Virtual environment not activating or dependencies not installing

**Solution**:
```bash
# Delete and recreate virtual environment
cd backend
rmdir /s venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 7. Frontend Build Errors

**Problem**: `npm install` or `npm run dev` fails

**Solution**:
```bash
# Clear npm cache and reinstall
cd frontend
npm cache clean --force
rmdir /s node_modules
del package-lock.json
npm install
```

### 8. Environment Variables Not Loading

**Problem**: Backend can't find environment variables

**Solution**:
1. Make sure `.env` file exists in `backend/` directory
2. Copy from template: `copy env.example backend\.env`
3. Edit the `.env` file with your settings
4. Restart the backend server

### 9. CORS Errors

**Problem**: Frontend can't connect to backend due to CORS

**Solution**:
1. Check if backend is running on port 5001
2. Verify CORS settings in `backend/app/core/config.py`
3. Make sure frontend is running on port 5173
4. Check browser console for specific error messages

### 10. AI Features Not Working

**Problem**: Gemini AI features not working

**Solution**:
1. Get Google AI API key from [makersuite.google.com](https://makersuite.google.com)
2. Add to `backend/.env`:
   ```env
   GEMINI_API_KEY=your-actual-api-key-here
   ```
3. Restart the backend server

## 🔧 Debugging Steps

### 1. Check Backend Status
```bash
# Test backend health
curl http://localhost:5001/api/health

# Check API documentation
# Open: http://localhost:5001/docs
```

### 2. Check Frontend Status
```bash
# Test frontend
# Open: http://localhost:5173
```

### 3. Check Logs
- Backend logs appear in the terminal where you started it
- Frontend logs appear in the terminal where you started it
- Check browser console (F12) for frontend errors

### 4. Verify Dependencies
```bash
# Backend dependencies
cd backend
venv\Scripts\activate
pip list

# Frontend dependencies
cd frontend
npm list
```

## 🆘 Getting Help

### 1. Check Documentation
- Main README: `README.md`
- Quick Start: `docs/QUICK_START.md`
- Project Structure: `docs/PROJECT_STRUCTURE.md`

### 2. Verify Prerequisites
- Python 3.8+ installed and in PATH
- Node.js 18+ installed and in PATH
- MongoDB running
- All environment variables set

### 3. Use Startup Scripts
- `scripts\start-full-stack.bat` - Start both servers
- `scripts\start-backend.bat` - Start backend only
- `scripts\start-frontend.bat` - Start frontend only
- `scripts\setup-project.bat` - Initial setup

### 4. Common Commands
```bash
# Start everything
scripts\start-full-stack.bat

# Start individually
scripts\start-backend.bat
scripts\start-frontend.bat

# Setup (first time)
scripts\setup-project.bat

# Fix imports
scripts\fix-backend-imports.bat
```

## 📞 Still Having Issues?

1. **Check the logs** in your terminal
2. **Verify all prerequisites** are installed
3. **Use the startup scripts** instead of manual commands
4. **Check the API documentation** at http://localhost:5001/docs
5. **Review the project structure** in `docs/PROJECT_STRUCTURE.md`

## ✅ Success Indicators

When everything is working correctly, you should see:

- **Backend**: "FastAPI Backend Started Successfully" in terminal
- **Frontend**: "Local: http://localhost:5173" in terminal
- **API Docs**: http://localhost:5001/docs loads successfully
- **Frontend**: http://localhost:5173 loads the application
