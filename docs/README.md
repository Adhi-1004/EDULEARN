# modLRN — AI-powered Adaptive Learning Platform

A comprehensive full-stack educational platform that combines modern web technologies with artificial intelligence to create an intelligent learning ecosystem.

## 🏗️ Project Structure

```
edulearn/
├── backend/                 # FastAPI backend application
│   ├── app/                # Main application package
│   │   ├── api/           # API endpoints (routers)
│   │   │   ├── admin.py
│   │   │   ├── assessments.py
│   │   │   ├── auth.py
│   │   │   ├── coding.py
│   │   │   ├── notifications.py
│   │   │   ├── results.py
│   │   │   ├── teacher.py
│   │   │   ├── topics.py
│   │   │   └── users.py
│   │   ├── core/          # Configuration and security
│   │   │   ├── config.py
│   │   │   └── security.py
│   │   ├── db/            # Database session management
│   │   │   ├── mock_db.py
│   │   │   └── session.py
│   │   ├── models/        # Database ORM models
│   │   │   └── models.py
│   │   ├── schemas/       # Pydantic schemas for validation
│   │   │   └── schemas.py
│   │   ├── services/      # Business logic
│   │   │   ├── code_execution_service.py
│   │   │   ├── gemini_coding_service.py
│   │   │   └── judge0_execution_service.py
│   │   ├── utils/         # Utility functions
│   │   │   ├── auth_utils.py
│   │   │   └── validators.py
│   │   ├── dependencies.py # FastAPI dependencies
│   │   └── main.py        # FastAPI app instance
│   ├── main.py           # Application entry point
│   ├── requirements.txt  # Python dependencies
│   ├── env.example       # Environment configuration template
│   └── venv/             # Python virtual environment
│
├── frontend/             # React frontend application
│   ├── src/              # Source code
│   │   ├── api/          # Centralized API services
│   │   │   ├── authService.ts
│   │   │   ├── assessmentService.ts
│   │   │   ├── codingService.ts
│   │   │   └── index.ts
│   │   ├── components/   # Reusable UI components
│   │   │   ├── admin/    # Admin-specific components
│   │   │   ├── teacher/  # Teacher-specific components
│   │   │   └── ui/       # Basic UI components
│   │   ├── contexts/     # React contexts
│   │   ├── hooks/        # Custom React hooks
│   │   ├── pages/         # Page components
│   │   ├── services/      # Business logic services
│   │   ├── types/         # TypeScript type definitions
│   │   └── utils/         # Utility functions
│   ├── package.json      # Frontend dependencies
│   ├── package-lock.json  # Dependency lock file
│   ├── tsconfig.json     # TypeScript configuration
│   ├── vite.config.js    # Vite configuration
│   ├── tailwind.config.js # Tailwind CSS configuration
│   ├── eslint.config.js  # ESLint configuration
│   ├── postcss.config.cjs # PostCSS configuration
│   └── index.html        # HTML entry point
│
├── docs/                 # Documentation
│   ├── COMPLETE_API_REFERENCE.md # Complete API endpoint mapping
│   ├── PROJECT_STRUCTURE.md
│   ├── QUICK_START.md
│   ├── README.md
│   ├── API_DOCUMENTATION.md
│   ├── ARCHITECTURE.md
│   ├── DATABASE_SCHEMA.md
│   ├── FEATURES.md
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

The backend provides a comprehensive REST API with over 100+ endpoints. For complete API documentation, see:

📘 **[Complete API Reference](./COMPLETE_API_REFERENCE.md)** - Comprehensive documentation of all API endpoints with request/response examples, frontend-backend mapping, and usage guides.

**Quick Reference:**
- **Authentication**: `/auth/*` - Login, register, OAuth, face recognition
- **User Management**: `/api/users/*` - Profile, gamification, badges
- **Assessments**: `/api/assessments/*` - Create, submit, leaderboards
- **Coding Platform**: `/api/coding/*` - Problems, execution, analytics
- **Teacher Dashboard**: `/api/teacher/*` - Batches, students, reports
- **Admin Dashboard**: `/api/admin/*` - User management, analytics
- **Notifications**: `/api/notifications/*` - Get, mark as read, delete
- **Bulk Operations**: `/bulk-students/*`, `/bulk-teachers/*` - Bulk uploads
- **Health Checks**: `/health/*` - System health monitoring
- **AI Questions**: `/api/ai-questions/*` - AI-generated question management
- **Topics**: `/api/topic/*` - Assessment configuration
- **Results**: `/api/results/*` - Assessment results and analytics

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

## 📚 Documentation

Complete documentation is available in the `/docs` directory:

- **[Complete API Reference](./COMPLETE_API_REFERENCE.md)** - All API endpoints with examples
- **[Quick Start Guide](./QUICK_START.md)** - Get started in 5 minutes
- **[Architecture Overview](./ARCHITECTURE.md)** - System architecture and design
- **[Database Schema](./DATABASE_SCHEMA.md)** - MongoDB collections and models
- **[Features Guide](./FEATURES.md)** - Complete feature documentation
- **[Project Structure](./PROJECT_STRUCTURE.md)** - Codebase organization
- **[API Documentation](./API_DOCUMENTATION.md)** - Additional API docs
- **[MongoDB Setup](./setup_mongodb.md)** - Database setup guide

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation in the `/docs` directory
- Review the [Complete API Reference](./COMPLETE_API_REFERENCE.md) for API details
- Check the FastAPI interactive docs at `http://localhost:5001/docs` when running the backend

---

**modLRN** - Empowering education through AI-driven adaptive learning.