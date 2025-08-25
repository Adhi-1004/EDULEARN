# 🚀 EduLearn AI v3 - Startup Guide

## Quick Start

### Option 1: Using Batch Files (Windows)
1. **Start Backend**: Double-click `start_backend.bat`
2. **Start Frontend**: Double-click `start_frontend.bat`
3. **Open Browser**: Navigate to `http://localhost:5173`

### Option 2: Manual Startup
1. **Backend**: `cd Backend && python app.py`
2. **Frontend**: `npm run dev`
3. **Browser**: Open `http://localhost:5173`

## 🔧 Prerequisites

### Required Software
- **Python 3.8+** - [Download Python](https://python.org)
- **Node.js 16+** - [Download Node.js](https://nodejs.org)
- **Git** - [Download Git](https://git-scm.com)

### Verify Installation
```bash
python --version    # Should show Python 3.8+
node --version     # Should show Node.js 16+
npm --version      # Should show npm version
```

## 📦 Installation Steps

### 1. Install Backend Dependencies
```bash
cd Backend
pip install -r requirements.txt
```

### 2. Install Frontend Dependencies
```bash
npm install
```

### 3. Verify Gemini AI Setup
The system uses Google Gemini AI. The API key is configured in the backend.

## 🚀 Starting the System

### Step 1: Start Backend Server
```bash
cd Backend
python app.py
```
**Expected Output:**
```
🚀 EDULEARNAI BACKEND SERVER STARTING
⏰ Started at: [timestamp]
🌐 Server will run on: http://0.0.0.0:5003
📝 Debug logs will be saved to: api_debug.log
🔍 All API requests will be logged with detailed information
```

### Step 2: Start Frontend Development Server
```bash
npm run dev
```
**Expected Output:**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h to show help
```

### Step 3: Access the Application
1. Open your browser
2. Navigate to `http://localhost:5173`
3. You should see the EduLearn AI homepage

## 🧪 Testing the System

### Test MCQ Assessment
1. Click "Login" or "Register"
2. Navigate to Student Dashboard
3. Click "MCQ Tests" tab
4. Click "Start New Assessment"
5. Fill in the form and start assessment

### Test Coding Environment
1. Navigate to Student Dashboard
2. Click "Coding Tests" tab
3. Click "Start Practice" on any problem
4. Write and test code

### Test Backend APIs
```bash
# Test MCQ generation
curl -X POST http://localhost:5003/getQuestions \
  -H "Content-Type: application/json" \
  -d '{"Topic": "Python", "Type": "MCQ", "Quantity": 5}'

# Test chatbot
curl -X POST http://localhost:5003/ChatBot \
  -H "Content-Type: application/json" \
  -d '{"Message": "Hello"}'
```

## 🔍 Troubleshooting

### Common Issues

#### Backend Won't Start
**Error**: `ModuleNotFoundError: No module named 'google.generativeai'`
**Solution**: 
```bash
cd Backend
pip install google-generativeai
```

**Error**: `ImportError: attempted relative import with no known parent package`
**Solution**: Fixed in the code - use absolute imports

**Error**: `Port already in use`
**Solution**: 
```bash
# Windows
netstat -ano | findstr :5003
taskkill /PID [PID] /F

# Linux/Mac
lsof -i :5003
kill -9 [PID]
```

#### Frontend Won't Start
**Error**: `EADDRINUSE: address already in use :::5173`
**Solution**: 
```bash
# Windows
netstat -ano | findstr :5173
taskkill /PID [PID] /F

# Linux/Mac
lsof -i :5173
kill -9 [PID]
```

**Error**: `Cannot find module`
**Solution**: 
```bash
rm -rf node_modules package-lock.json
npm install
```

### Performance Issues
- **Slow MCQ Generation**: Check Gemini AI API response times
- **Frontend Lag**: Ensure sufficient RAM (4GB+ recommended)
- **Backend Timeout**: Check network connectivity to Gemini AI

## 📊 System Status

### Backend Health Check
- **URL**: `http://localhost:5003/getQuestions`
- **Method**: GET
- **Expected**: `{"Reply": "Hosted successfully"}`

### Frontend Health Check
- **URL**: `http://localhost:5173`
- **Expected**: EduLearn AI homepage loads

### API Endpoints Status
- ✅ `/getQuestions` - MCQ generation
- ✅ `/getQuizFeedback` - Assessment feedback
- ✅ `/coding/generate` - Coding problems
- ✅ `/coding/evaluate` - Code evaluation
- ✅ `/ChatBot` - AI assistant

## 🔐 Security Notes

- **API Key**: Gemini AI key is configured in backend
- **CORS**: Configured for development (allows all origins)
- **Validation**: Input validation on all endpoints
- **Logging**: All requests are logged for debugging

## 📝 Development Notes

### File Structure
```
edulearn_v3/
├── Backend/           # Flask backend
│   ├── app.py        # Main Flask application
│   ├── llm_api.py    # Gemini AI integration
│   ├── prompts.py    # AI prompt templates
│   └── requirements.txt
├── src/              # React frontend
│   ├── pages/        # Page components
│   ├── components/   # Reusable components
│   └── contexts/     # React contexts
├── start_backend.bat # Backend startup script
├── start_frontend.bat # Frontend startup script
└── README.md         # Main documentation
```

### Key Components
- **MCQ Assessment**: `src/pages/student/MCQAssessment.jsx`
- **Results Page**: `src/pages/student/ResultsPage.jsx`
- **Coding Environment**: `src/pages/student/CodingEnvironment.tsx`
- **Student Dashboard**: `src/pages/student/StudentDashboard.tsx`

## 🎯 Next Steps

After successful startup:
1. **Explore Features**: Try all assessment types
2. **Customize Content**: Modify prompts and questions
3. **Add Users**: Implement user management
4. **Deploy**: Prepare for production deployment

## 📞 Support

If you encounter issues:
1. Check this startup guide
2. Review the main README.md
3. Check console logs for errors
4. Verify all dependencies are installed
5. Ensure ports are available

---

**Happy Learning with EduLearn AI! 🚀**
