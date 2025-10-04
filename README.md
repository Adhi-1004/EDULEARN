# modLRN — AI-powered Adaptive Learning Platform

A comprehensive full-stack educational platform that combines modern web technologies with artificial intelligence to create an intelligent learning ecosystem.

## 🏗️ Project Structure

```
edulearn/
├── frontend/                 # React frontend application
│   ├── public/             # Static assets
│   ├── src/
│   │   ├── api/           # Centralized API services
│   │   │   ├── authService.ts
│   │   │   ├── assessmentService.ts
│   │   │   ├── codingService.ts
│   │   │   └── index.ts
│   │   ├── assets/        # Images, fonts, etc.
│   │   ├── components/    # Reusable UI components
│   │   ├── contexts/      # React contexts
│   │   ├── hooks/         # Custom React hooks
│   │   ├── pages/         # Page components
│   │   ├── types/         # TypeScript type definitions
│   │   └── utils/         # Utility functions
│   ├── .eslintrc.cjs      # ESLint configuration
│   ├── .gitignore        # Frontend-specific gitignore
│   ├── index.html        # HTML entry point
│   ├── package.json      # Frontend dependencies
│   ├── tsconfig.json     # TypeScript configuration
│   └── vite.config.js    # Vite configuration
│
├── backend/               # FastAPI backend application
│   ├── app/              # Main application package
│   │   ├── api/          # API endpoints (routers)
│   │   │   ├── endpoints/
│   │   │   │   ├── auth.py
│   │   │   │   ├── assessments.py
│   │   │   │   └── coding.py
│   │   │   └── ...
│   │   ├── core/         # Configuration and security
│   │   │   ├── config.py
│   │   │   └── security.py
│   │   ├── db/           # Database session management
│   │   │   └── session.py
│   │   ├── models/       # Database ORM models
│   │   ├── schemas/      # Pydantic schemas for validation
│   │   ├── services/     # Business logic
│   │   ├── tests/        # Backend tests
│   │   ├── utils/        # Utility functions
│   │   └── main.py       # FastAPI app instance
│   ├── .gitignore       # Backend-specific gitignore
│   └── requirements.txt  # Backend dependencies
│
├── .gitignore            # Root gitignore
└── README.md            # Project-wide README
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
cp .env.example .env
# Edit .env with your configuration

# Run the backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 5001
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

- **Authentication**: `/auth/*`
- **User Management**: `/db/*`
- **Assessments**: `/api/assessments/*`
- **Coding Platform**: `/api/coding/*`
- **Code Execution**: `/api/execute/*`
- **Teacher Dashboard**: `/api/teacher/*`
- **Admin Dashboard**: `/api/admin/*`

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

---

**modLRN** - Empowering education through AI-driven adaptive learning.