# modLRN Backend

FastAPI backend for the modLRN AI-powered Adaptive Learning Platform.

## 🏗️ Architecture

The backend follows a clean, modular architecture:

```
backend/
├── app/                   # Main application package
│   ├── api/              # API endpoints (routers)
│   │   ├── endpoints/    # Organized endpoint files
│   │   │   ├── auth.py   # Authentication endpoints
│   │   │   ├── assessments.py  # Assessment management
│   │   │   └── coding.py # Coding platform endpoints
│   │   ├── users.py      # User management
│   │   ├── questions.py  # Question management
│   │   ├── results.py    # Results and analytics
│   │   └── ...
│   ├── core/             # Configuration and security
│   │   ├── config.py     # Application settings
│   │   └── security.py   # Security utilities
│   ├── db/               # Database session management
│   │   └── session.py    # MongoDB connection
│   ├── models/           # Database ORM models
│   ├── schemas/          # Pydantic schemas for validation
│   ├── services/         # Business logic
│   ├── tests/            # Backend tests
│   ├── utils/            # Utility functions
│   └── main.py           # FastAPI app instance
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- MongoDB
- Google AI API key (for Gemini integration)

### Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

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

### Running the Server

```bash
# Development mode
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 5001

# Production mode
python -m uvicorn app.main:app --host 0.0.0.0 --port 5001
```

## 🛠️ Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **MongoDB**: NoSQL database with Motor async driver
- **Pydantic**: Data validation and serialization
- **JWT**: JSON Web Tokens for authentication
- **Google Gemini AI**: AI-powered question generation
- **Face Recognition**: Biometric authentication
- **Code Execution**: Sandboxed multi-language execution

## 📚 API Documentation

When the server is running, visit:
- **Swagger UI**: `http://localhost:5001/docs`
- **ReDoc**: `http://localhost:5001/redoc`

## 🧪 Testing

```bash
# Run all tests
python -m pytest app/tests/

# Run specific test file
python -m pytest app/tests/test_coding_endpoints.py

# Run with coverage
python -m pytest app/tests/ --cov=app
```

## 🔧 Development

### Code Structure

- **API Endpoints**: Organized by functionality in `app/api/`
- **Database Models**: MongoDB document models in `app/models/`
- **Pydantic Schemas**: Request/response validation in `app/schemas/`
- **Business Logic**: Service layer in `app/services/`
- **Utilities**: Helper functions in `app/utils/`

### Adding New Endpoints

1. Create router in `app/api/` or `app/api/endpoints/`
2. Import and include in `app/main.py`
3. Add appropriate authentication and validation
4. Write tests in `app/tests/`

### Database Operations

```python
from app.db import get_db

# Get database instance
db = await get_db()

# Example operations
users = await db.users.find().to_list(None)
user = await db.users.find_one({"email": "user@example.com"})
```

## 🚀 Deployment

### Environment Variables

Ensure all required environment variables are set:

```env
MONGO_URI=mongodb://your-mongo-host:27017
DB_NAME=edulearn
SECRET_KEY=your-secret-key
GEMINI_API_KEY=your-gemini-api-key
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### Production Considerations

- Use a production ASGI server like Gunicorn
- Set up proper logging
- Configure CORS for your frontend domain
- Use environment-specific configurations
- Set up monitoring and health checks

## 📝 API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/google-login` - Google OAuth login
- `POST /auth/face-login` - Face recognition login
- `GET /auth/me` - Get current user

### User Management
- `GET /db/users` - Get all users
- `GET /db/users/{user_id}` - Get user by ID
- `PUT /db/users/{user_id}` - Update user
- `DELETE /db/users/{user_id}` - Delete user

### Assessments
- `POST /api/assessments/` - Create assessment
- `GET /api/assessments/` - Get assessments
- `POST /api/assessments/{id}/questions` - Add questions
- `POST /api/assessments/{id}/submit` - Submit assessment

### Coding Platform
- `POST /api/coding/problems/generate` - Generate AI problem
- `GET /api/coding/problems` - Get problems
- `POST /api/coding/execute` - Execute code
- `POST /api/coding/submit` - Submit solution

## 🆘 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all `__init__.py` files are present
2. **Database Connection**: Check MongoDB is running and accessible
3. **Authentication**: Verify JWT secret key is set
4. **AI Services**: Ensure Gemini API key is configured

### Logs

The application provides detailed logging:
- Startup logs show configuration status
- API requests are logged with timestamps
- Errors include full stack traces

## 🤝 Contributing

1. Follow the existing code structure
2. Add appropriate error handling
3. Write tests for new functionality
4. Update documentation as needed
5. Follow Python best practices

---

**modLRN Backend** - Powering the future of adaptive learning.
