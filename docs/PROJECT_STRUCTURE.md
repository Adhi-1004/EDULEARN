# modLRN Project Structure

## 📁 Complete Directory Structure

```
edulearn/
├── backend/                    # FastAPI Backend Application
│   ├── app/                   # Main application package
│   │   ├── api/              # API endpoints (routers)
│   │   │   ├── endpoints/    # Organized endpoint files
│   │   │   │   ├── auth.py   # Authentication endpoints
│   │   │   │   ├── assessments.py  # Assessment management
│   │   │   │   └── coding.py # Coding platform endpoints
│   │   │   ├── users.py      # User management
│   │   │   ├── questions.py  # Question management
│   │   │   ├── results.py    # Results and analytics
│   │   │   └── ...           # Other API modules
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
│   │   ├── tests/            # Backend tests
│   │   │   ├── test_coding_endpoints.py
│   │   │   └── test_role_based_access.py
│   │   ├── utils/            # Utility functions
│   │   │   └── auth_utils.py  # Authentication utilities
│   │   ├── dependencies.py   # FastAPI dependencies
│   │   └── main.py          # FastAPI app instance
│   ├── venv/                 # Python virtual environment
│   ├── requirements.txt      # Python dependencies
│   ├── env.example          # Environment configuration template
│   └── README.md            # Backend documentation
│
├── frontend/                 # React Frontend Application
│   ├── src/                 # Source code
│   │   ├── api/             # Centralized API services
│   │   │   ├── authService.ts      # Authentication operations
│   │   │   ├── assessmentService.ts # Assessment management
│   │   │   ├── codingService.ts    # Coding platform functionality
│   │   │   └── index.ts            # Service exports
│   │   ├── components/       # Reusable UI components
│   │   │   ├── ui/          # Basic UI components
│   │   │   ├── admin/       # Admin-specific components
│   │   │   ├── teacher/     # Teacher-specific components
│   │   │   └── ...          # Feature-specific components
│   │   ├── contexts/        # React contexts
│   │   │   ├── ThemeContext.tsx    # Theme management
│   │   │   └── ToastContext.tsx    # Notification system
│   │   ├── hooks/           # Custom React hooks
│   │   │   └── useAuth.ts          # Authentication hook
│   │   ├── pages/           # Page components
│   │   │   ├── Dashboard.tsx       # Student dashboard
│   │   │   ├── CodingPlatform.tsx # Coding challenges
│   │   │   ├── TeacherDashboard.tsx # Teacher interface
│   │   │   └── ...          # Other pages
│   │   ├── services/        # Business logic services
│   │   │   └── mockDataService.ts  # Mock data for development
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
│   ├── dist/                # Production build output
│   ├── node_modules/        # Node.js dependencies
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
├── scripts/                 # Startup and Utility Scripts
│   ├── start-backend.bat        # Start backend server (Windows)
│   ├── start-backend.ps1        # Start backend server (PowerShell)
│   ├── start-frontend.bat      # Start frontend server (Windows)
│   ├── start-frontend.ps1      # Start frontend server (PowerShell)
│   ├── start-full-stack.bat    # Start both servers (Windows)
│   ├── setup-project.bat       # Initial project setup
│   ├── setup_mongodb.bat        # MongoDB setup script
│   ├── start_backend.py         # Python backend starter
│   ├── start_server.bat         # Legacy server starter
│   ├── start_server_fixed.bat  # Fixed server starter
│   ├── clear_and_create_admin.py    # Admin management
│   ├── create_admin_user.py         # Admin user creation
│   ├── fix_admin_auth.py            # Admin auth fixes
│   ├── fix_admin.py                 # Admin fixes
│   ├── reset_admin.py               # Admin reset
│   ├── reset_original_admin.py     # Original admin reset
│   ├── init_badges.py               # Badge initialization
│   ├── main.py                      # Main script
│   └── mockDataService.ts           # Mock data service
│
├── docs/                    # Documentation Files
│   ├── DASHBOARD_VERIFICATION.md
│   ├── ENHANCED_DASHBOARD_README.md
│   ├── fix_auth.md
│   ├── FIX_LOGIN_ISSUE.md
│   ├── IMPLEMENTATION_SUMMARY.md
│   ├── PROJECT_STRUCTURE.md         # This file
│   ├── QUICK_START.md               # Quick start guide
│   ├── RBAC_IMPLEMENTATION.md
│   ├── README.md                    # Backend README
│   └── setup_mongodb.md
│
├── tests/                   # Integration Tests
│   ├── test_admin_auth.py
│   ├── test_complete_admin_flow.py
│   ├── test_frontend_backend_connection.py
│   ├── test_frontend_admin_auth.html
│   ├── test_login.py
│   ├── test_rbac_quick.py
│   └── test_rbac_system.py
│
├── env.example              # Environment configuration template
└── README.md                # Main project documentation
```

## 🎯 Key Directories Explained

### Backend (`/backend/`)
- **FastAPI application** with modular structure
- **API endpoints** organized by functionality
- **Database models** and **schemas** for data validation
- **Services** for business logic
- **Tests** for backend functionality

### Frontend (`/frontend/`)
- **React 18** with **TypeScript**
- **Component-based** architecture
- **API services** for backend communication
- **Context providers** for state management
- **Responsive design** with Tailwind CSS

### Scripts (`/scripts/`)
- **Startup scripts** for development
- **Setup scripts** for initial configuration
- **Utility scripts** for maintenance
- **Cross-platform** support (Windows batch and PowerShell)

### Documentation (`/docs/`)
- **Project documentation**
- **Setup guides**
- **Implementation details**
- **Troubleshooting guides**

### Tests (`/tests/`)
- **Integration tests**
- **End-to-end tests**
- **Authentication tests**
- **RBAC system tests**

## 🚀 Quick Navigation

### Start Development
```bash
# Start both servers
scripts\start-full-stack.bat

# Or start individually
scripts\start-backend.bat
scripts\start-frontend.bat
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

1. **Setup**: Run `scripts\setup-project.bat`
2. **Configure**: Copy `env.example` to `backend\.env`
3. **Start**: Run `scripts\start-full-stack.bat`
4. **Develop**: Edit code in `backend/app/` or `frontend/src/`
5. **Test**: Run tests in `backend/app/tests/` or `frontend/`
6. **Build**: Use `npm run build` for frontend production

## 🔧 Maintenance

- **Dependencies**: Update `requirements.txt` and `package.json`
- **Environment**: Update `env.example` for new variables
- **Documentation**: Update files in `docs/`
- **Scripts**: Add new utilities to `scripts/`
