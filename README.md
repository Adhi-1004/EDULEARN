# modLRN — AI-powered Adaptive Learning Platform

A comprehensive full-stack educational platform that combines modern web technologies with artificial intelligence to create an intelligent learning ecosystem.

## 🏗️ Project Structure

```
edulearn/
├── backend/                 # FastAPI backend application
│   ├── app/                # Main application package
│   │   ├── api/           # API endpoints (routers)
│   │   ├── core/          # Configuration and security
│   │   ├── db/            # Database session management
│   │   ├── models/        # Database ORM models
│   │   ├── schemas/       # Pydantic schemas for validation
│   │   ├── services/      # Business logic
│   │   └── utils/         # Utility functions
│   ├── main.py           # Application entry point
│   ├── requirements.txt  # Python dependencies
│   └── venv/             # Python virtual environment
│
├── frontend/             # React frontend application
│   ├── src/              # Source code
│   │   ├── api/          # Centralized API services
│   │   ├── components/   # Reusable UI components
│   │   ├── contexts/     # React contexts
│   │   ├── hooks/        # Custom React hooks
│   │   ├── pages/         # Page components
│   │   ├── services/      # Business logic services
│   │   ├── types/         # TypeScript type definitions
│   │   └── utils/         # Utility functions
│   ├── package.json      # Frontend dependencies
│   └── [config files]    # Vite, TypeScript, Tailwind, etc.
│
├── docs/                 # Documentation
│   ├── PROJECT_STRUCTURE.md
│   ├── QUICK_START.md
│   ├── README.md
│   └── setup_mongodb.md
│
├── scripts/              # Utility scripts (cleaned)
├── PROJECT_STRUCTURE.md  # Project structure overview
└── README.md            # Main project documentation
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm/yarn
- Python 3.8+
- MongoDB
- Google AI API key (for Gemini integration)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env with your configuration

# Run the backend
python main.py
```

### Frontend Setup

```bash
cd frontend
npm install

# Run the frontend
npm run dev
```

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI 0.104.1
- **Database**: MongoDB with Motor (async Python driver)
- **Authentication**: JWT, Google OAuth, Face recognition
- **AI Integration**: Google Gemini AI
- **Code Execution**: Sandboxed multi-language execution
- **Validation**: Pydantic models

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: React Context API
- **Routing**: React Router DOM
- **Code Editor**: Monaco Editor
- **Animations**: Framer Motion
- **HTTP Client**: Axios

## 🎯 Key Features

### For Students
- **AI-Powered Assessments**: Dynamic question generation using Gemini AI
- **Adaptive Learning**: Personalized learning paths based on performance
- **Coding Platform**: Interactive coding challenges with real-time execution
- **Progress Tracking**: Detailed analytics and performance insights
- **Multiple Authentication**: Email/password, Google OAuth, and face recognition

### For Teachers
- **Assessment Creation**: AI-assisted question generation
- **Batch Management**: Organize students into learning groups
- **Analytics Dashboard**: Track student progress and performance
- **Content Management**: Oversee and moderate AI-generated content

### For Administrators
- **User Management**: Comprehensive user administration
- **System Analytics**: Platform-wide statistics and insights
- **Content Oversight**: Monitor and manage AI-generated content
- **Role-based Access**: Granular permission system

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Database
MONGO_URI=mongodb://localhost:27017
DB_NAME=edulearn

# Security
SECRET_KEY=your-secret-key-here

# AI Services
GEMINI_API_KEY=your-google-ai-api-key

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### API Endpoints

The backend provides a comprehensive REST API:

- **Authentication**: `/auth/*` and `/api/auth/*`
- **User Management**: `/users/*` and `/api/users/*`
- **Assessments**: `/assessments/*` and `/api/assessments/*`
- **Coding Platform**: `/coding/*` and `/api/coding/*`
- **Teacher Dashboard**: `/teacher/*` and `/api/teacher/*`
- **Admin Dashboard**: `/admin/*` and `/api/admin/*`
- **Topics**: `/topics/*` and `/api/topics/*`
- **Results**: `/results/*` and `/api/results/*`

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest app/tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📦 Deployment

### Backend Deployment
The backend can be deployed to any platform that supports Python/FastAPI:
- **Render**: Easy deployment with automatic builds
- **Railway**: Simple containerized deployment
- **Heroku**: Traditional platform deployment
- **Docker**: Containerized deployment

### Frontend Deployment
The frontend can be deployed to any static hosting platform:
- **Vercel**: Optimized for React applications
- **Netlify**: Simple static site deployment
- **GitHub Pages**: Free hosting for public repositories

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Development Team**: modLRN Development Team
- **AI Integration**: Google Gemini AI
- **UI/UX**: Modern React patterns with Tailwind CSS

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation in the `/docs` directory
- Review the API documentation at `/docs` when running the backend

## 🧹 Recent Cleanup

The project has been recently cleaned up to remove:
- ✅ All `__pycache__` directories
- ✅ Test files and directories
- ✅ Batch and PowerShell scripts
- ✅ Duplicate files
- ✅ Unnecessary documentation
- ✅ Build artifacts (`node_modules`, `dist`)
- ✅ Redundant scripts

The project now has a **clean, professional structure** ready for development and deployment.

---

**modLRN** - Empowering education through AI-driven adaptive learning.