# modLRN - Quick Start Guide

## 🚀 Commands to Run the Project

### Prerequisites
- Python 3.8+ installed
- Node.js 18+ installed  
- MongoDB running locally
- Google AI API key (optional for AI features)

### 1. Initial Setup (First Time Only)

**Backend Setup:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # On Windows
# or
source venv/bin/activate  # On Linux/Mac
pip install -r requirements.txt
```

**Frontend Setup:**
```bash
cd frontend
npm install
```

### 2. Configure Environment

```bash
# Copy environment template
cp env.example backend/.env

# Edit the .env file with your settings
# At minimum, set:
# - SECRET_KEY (generate a random string)
# - GEMINI_API_KEY (for AI features)
```

### 3. Start the Application

#### Option A: Start Both Servers (Recommended)

**Backend (Terminal 1):**
```bash
cd backend
venv\Scripts\activate
python main.py
```

**Frontend (Terminal 2):**
```bash
cd frontend
npm run dev
```

#### Option B: Manual Commands

**Backend:**
```bash
cd backend
venv\Scripts\activate
python main.py
```

**Frontend:**
```bash
cd frontend
npm run dev
```

## 🌐 Access Points

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:5001
- **API Documentation**: http://localhost:5001/docs
- **Health Check**: http://localhost:5001/api/health

## 🔧 Development Commands

### Backend Development
```bash
# CORRECT WAY - Run from backend directory
cd backend
venv\Scripts\activate
python main.py

# The server will start on http://localhost:5001
```

### Frontend Development
```bash
cd frontend
npm run dev

# The server will start on http://localhost:5173
```

### Running Tests
```bash
# Backend tests (if available)
cd backend
python -m pytest app/tests/

# Frontend tests
cd frontend
npm test
```

### Building for Production
```bash
# Frontend build
cd frontend
npm run build

# Backend (no build needed, just run)
cd backend
python main.py
```

## 🆘 Troubleshooting

### Common Issues

1. **Python not found**: Install Python 3.8+ from python.org
2. **Node.js not found**: Install Node.js 18+ from nodejs.org
3. **MongoDB connection failed**: Start MongoDB service
4. **Port already in use**: Kill processes using ports 5001/5173
5. **Dependencies failed**: Check internet connection and try again

### Environment Variables

Make sure these are set in `backend/.env`:
```env
MONGO_URI=mongodb://localhost:27017
DB_NAME=edulearn
SECRET_KEY=your-secret-key-here
GEMINI_API_KEY=your-google-ai-api-key
```

### Database Setup

1. Install MongoDB
2. Start MongoDB service
3. The app will create the database automatically

### AI Features Setup

1. Get Google AI API key from https://makersuite.google.com
2. Add it to `backend/.env` as `GEMINI_API_KEY`
3. Restart the backend server

## 📁 Project Structure

```
edulearn/
├── backend/           # FastAPI backend
│   ├── app/          # Main application
│   ├── main.py       # Entry point
│   ├── requirements.txt
│   └── venv/         # Virtual environment
├── frontend/         # React frontend  
│   ├── src/          # Source code
│   ├── package.json
│   └── node_modules/ # (after npm install)
├── docs/            # Documentation
├── scripts/         # Utility scripts (cleaned)
└── README.md        # Main documentation
```

## 🎯 Next Steps

1. **Configure Environment**: Set up your `.env` file
2. **Start MongoDB**: Ensure MongoDB is running
3. **Install Dependencies**: Run setup commands
4. **Start Application**: Run both servers
5. **Access Application**: Open http://localhost:5173

## 📞 Support

- Check the main README.md for detailed documentation
- Review API documentation at http://localhost:5001/docs
- Check logs in the terminal for error messages

## 🧹 Recent Cleanup

The project has been cleaned up and now features:
- ✅ **Clean structure** with no unnecessary files
- ✅ **No cache files** or build artifacts
- ✅ **Streamlined documentation**
- ✅ **Easy setup process**
- ✅ **Professional organization**

Your development environment is now ready for efficient coding!