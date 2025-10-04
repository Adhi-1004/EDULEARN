# modLRN Project Structure

## 📁 Complete Directory Structure

```
edulearn/
├── backend/                    # FastAPI Backend Application
│   ├── app/                   # Main application package
│   │   ├── api/              # API endpoints (routers)
│   │   │   ├── admin.py      # Admin dashboard endpoints
│   │   │   ├── assessments.py # Assessment management
│   │   │   ├── auth.py       # Authentication endpoints
│   │   │   ├── coding.py      # Coding platform endpoints
│   │   │   ├── notifications.py # Notification system
│   │   │   ├── results.py     # Results and analytics
│   │   │   ├── teacher.py     # Teacher dashboard
│   │   │   ├── topics.py     # Topics and AI questions
│   │   │   └── users.py       # User management
│   │   ├── core/             # Configuration and security
│   │   │   ├── config.py     # Application settings
│   │   │   └── security.py   # Security utilities
│   │   ├── db/               # Database session management
│   │   │   ├── session.py    # MongoDB connection
│   │   │   └── mock_db.py    # Mock database for testing
│   │   ├── models/           # Database ORM models
│   │   │   └── models.py     # MongoDB document models
│   │   ├── schemas/          # Pydantic schemas for validation
│   │   │   └── schemas.py    # Request/response validation
│   │   ├── services/         # Business logic
│   │   │   ├── code_execution_service.py
│   │   │   ├── gemini_coding_service.py
│   │   │   └── judge0_execution_service.py
│   │   ├── utils/            # Utility functions
│   │   │   ├── auth_utils.py  # Authentication utilities
│   │   │   └── validators.py  # Data validation utilities
│   │   ├── dependencies.py   # FastAPI dependencies
│   │   └── main.py          # FastAPI app instance
│   ├── main.py              # Application entry point
│   ├── requirements.txt     # Python dependencies
│   ├── env.example          # Environment configuration template
│   ├── README.md            # Backend documentation
│   └── venv/                # Python virtual environment
│
├── frontend/                 # React Frontend Application
│   ├── src/                 # Source code
│   │   ├── api/             # Centralized API services
│   │   │   ├── authService.ts      # Authentication operations
│   │   │   ├── assessmentService.ts   # Assessment management
│   │   │   ├── codingService.ts     # Coding platform functionality
│   │   │   └── index.ts             # Service exports
│   │   ├── components/       # Reusable UI components
│   │   │   ├── ui/          # Basic UI components
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Card.tsx
│   │   │   │   ├── Input.tsx
│   │   │   │   ├── LoadingSpinner.tsx
│   │   │   │   ├── Toast.tsx
│   │   │   │   └── ...
│   │   │   ├── admin/       # Admin-specific components
│   │   │   │   ├── ContentOversight.tsx
│   │   │   │   ├── EnhancedAdminDashboard.tsx
│   │   │   │   ├── SystemAnalytics.tsx
│   │   │   │   └── UserManagement.tsx
│   │   │   ├── teacher/     # Teacher-specific components
│   │   │   │   ├── AIStudentReports.tsx
│   │   │   │   ├── BatchPerformanceControl.tsx
│   │   │   │   └── SmartAssessmentCreator.tsx
│   │   │   ├── AnimatedBackground.tsx
│   │   │   ├── AssessmentResults.tsx
│   │   │   ├── BackendStatusIndicator.tsx
│   │   │   ├── CodingTestInterface.tsx
│   │   │   ├── FaceLogin.tsx
│   │   │   ├── GamificationPanel.tsx
│   │   │   ├── Leaderboard.tsx
│   │   │   ├── Navbar.tsx
│   │   │   ├── ProgressCharts.tsx
│   │   │   ├── ProtectedRoute.tsx
│   │   │   ├── StatsCard.tsx
│   │   │   └── TestInterface.tsx
│   │   ├── contexts/        # React contexts
│   │   │   ├── ThemeContext.tsx    # Theme management
│   │   │   └── ToastContext.tsx     # Notification system
│   │   ├── hooks/           # Custom React hooks
│   │   │   └── useAuth.ts          # Authentication hook
│   │   ├── pages/           # Page components
│   │   │   ├── AssessConfig.tsx       # Assessment configuration
│   │   │   ├── Assessment.tsx          # Assessment interface
│   │   │   ├── AssessmentChoice.tsx    # Assessment selection
│   │   │   ├── CodingPlatform.tsx     # Coding challenges
│   │   │   ├── CodingProblem.tsx      # Individual coding problem
│   │   │   ├── Dashboard.tsx          # Student dashboard
│   │   │   ├── LandingPage.tsx        # Landing page
│   │   │   ├── Login.tsx              # Login page
│   │   │   ├── Results.tsx            # Results page
│   │   │   ├── Settings.tsx           # User settings
│   │   │   ├── Signup.tsx             # Registration page
│   │   │   ├── TeacherDashboard.tsx   # Teacher interface
│   │   │   ├── TestPage.tsx           # Test interface
│   │   │   ├── TestResultDetail.tsx   # Detailed results
│   │   │   └── UserProfile.tsx        # User profile
│   │   ├── services/        # Business logic services
│   │   │   └── notificationService.ts  # Notification system
│   │   ├── types/           # TypeScript type definitions
│   │   │   └── index.ts            # Type exports
│   │   ├── utils/           # Utility functions
│   │   │   ├── api.ts              # API configuration
│   │   │   ├── constants.ts        # Application constants
│   │   │   └── roleUtils.ts        # Role-based utilities
│   │   ├── App.tsx          # Main App component
│   │   ├── main.tsx         # Application entry point
│   │   └── index.css        # Global styles
│   ├── public/              # Static assets
│   ├── package.json         # Frontend dependencies and scripts
│   ├── package-lock.json    # Dependency lock file
│   ├── tsconfig.json        # TypeScript configuration
│   ├── vite.config.js       # Vite configuration
│   ├── tailwind.config.js   # Tailwind CSS configuration
│   ├── eslint.config.js     # ESLint configuration
│   ├── postcss.config.cjs   # PostCSS configuration
│   ├── index.html           # HTML entry point
│   └── README.md            # Frontend documentation
│
├── docs/                    # Documentation Files
│   ├── PROJECT_STRUCTURE.md         # This file
│   ├── QUICK_START.md               # Quick start guide
│   ├── README.md                    # Main documentation
│   └── setup_mongodb.md             # MongoDB setup guide
│
├── scripts/                 # Utility Scripts (Cleaned)
│   └── (empty - cleaned during project cleanup)
│
├── env.example              # Environment configuration template
├── PROJECT_STRUCTURE.md     # Project structure overview
└── README.md                # Main project documentation
```

## 🎯 Key Directories Explained

### Backend (`/backend/`)
- **FastAPI application** with modular structure
- **API endpoints** organized by functionality
- **Database models** and **schemas** for data validation
- **Services** for business logic
- **Clean structure** with no test files or cache

### Frontend (`/frontend/`)
- **React 18** with **TypeScript**
- **Component-based** architecture
- **API services** for backend communication
- **Context providers** for state management
- **Responsive design** with Tailwind CSS

### Documentation (`/docs/`)
- **Essential documentation** only
- **Setup guides** and **quick start**
- **Project structure** overview
- **MongoDB setup** instructions

### Scripts (`/scripts/`)
- **Cleaned directory** (removed unnecessary files)
- **Ready for new utility scripts** if needed

## 🚀 Quick Navigation

### Start Development
```bash
# Backend
cd backend
python main.py

# Frontend (in new terminal)
cd frontend
npm run dev
```

### Access Points
- **Frontend**: http://localhost:5173
- **Backend**: http://localhost:5001
- **API Docs**: http://localhost:5001/docs

### Key Files
- **Main README**: `README.md`
- **Quick Start**: `docs/QUICK_START.md`
- **Backend Config**: `backend/env.example`
- **Frontend Config**: `frontend/package.json`

## 📋 Development Workflow

1. **Setup**: Follow the quick start guide
2. **Configure**: Copy `env.example` to `backend/.env`
3. **Start**: Run backend and frontend servers
4. **Develop**: Edit code in `backend/app/` or `frontend/src/`
5. **Test**: Use the built-in testing frameworks
6. **Build**: Use `npm run build` for frontend production

## 🔧 Maintenance

- **Dependencies**: Update `requirements.txt` and `package.json`
- **Environment**: Update `env.example` for new variables
- **Documentation**: Update files in `docs/`
- **Clean Structure**: Maintain the clean, organized structure

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