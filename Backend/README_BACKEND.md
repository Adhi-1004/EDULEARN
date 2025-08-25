# EduLearn AI Backend Documentation

## Overview

The EduLearn AI Backend is a comprehensive Flask-based REST API that powers both student and teacher dashboards with AI-enhanced educational features.

## Features

### 🎓 Student Features
- **Assignments**: View, submit, and track assignment progress
- **Study Materials**: Access lectures, PDFs, videos, and other resources
- **Virtual Labs**: Interactive simulations and experiments
- **Discussions**: Forum-style discussions by subject
- **Study Groups**: Collaborative learning groups
- **Projects**: Personal and group project management
- **Notes**: Personal note-taking system
- **Notifications**: Real-time updates and reminders
- **Analytics**: Personal performance tracking and insights
- **MCQ Assessments**: AI-generated multiple choice questions
- **Coding Practice**: AI-generated programming problems
- **Leaderboard**: Competition and ranking system

### 👨‍🏫 Teacher Features
- **Assignment Management**: Create and manage assignments
- **Submission Reviews**: Review and grade student submissions
- **Class Analytics**: Comprehensive class performance metrics
- **Student Progress**: Individual student tracking
- **Grade Distribution**: Visual analytics and reports
- **Performance Trends**: Historical performance analysis
- **Content Creation**: Upload and manage study materials

### 🤖 AI Integration
- **Question Generation**: MCQ and coding problems via Gemini AI
- **Automated Feedback**: AI-powered assessment and suggestions
- **Personalized Recommendations**: Adaptive learning paths
- **Performance Analytics**: AI-driven insights and predictions
- **Code Evaluation**: Automated code assessment

## Installation

### Prerequisites
- Python 3.8+
- MongoDB (local or cloud)
- Google Gemini API key

### Setup Steps

1. **Install Dependencies**
```bash
cd Backend
pip install -r requirements.txt
```

2. **Environment Configuration**
Create a `.env` file:
```env
GEMINI_API_KEY=your_gemini_api_key_here
MONGO_URI=mongodb://localhost:27017/edulearn_ai
```

3. **Start MongoDB**
```bash
# Local MongoDB
mongod

# Or use MongoDB Atlas (cloud)
```

4. **Run the Server**
```bash
python app.py
```

The server will start at `http://localhost:5003`

## API Endpoints

### Authentication
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/register` | POST | Register new user |
| `/auth/login` | POST | User login |
| `/user/profile` | GET/PUT | Get/update user profile |

### Student Dashboard
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/student/assignments` | GET | Get student assignments |
| `/student/submissions` | GET/POST | View/create submissions |
| `/student/projects` | GET/POST | Manage projects |
| `/student/notes` | GET/POST | Personal notes |
| `/student/analytics` | GET | Performance analytics |
| `/materials` | GET/POST | Study materials |
| `/labs` | GET/POST | Virtual labs |
| `/discussions` | GET/POST | Discussion forums |
| `/groups` | GET/POST | Study groups |
| `/notifications` | GET/POST | User notifications |

### Teacher Dashboard
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/teacher/assignments` | GET/POST | Manage assignments |
| `/teacher/submissions` | GET | Review submissions |
| `/teacher/analytics` | GET | Class analytics |

### AI Features
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/getQuestions` | POST | Generate MCQ questions |
| `/getQuizFeedback` | POST | Get quiz feedback |
| `/coding/generate` | POST | Generate coding problems |
| `/coding/evaluate` | POST | Evaluate code solutions |
| `/ChatBot` | POST | AI chatbot interaction |
| `/ai/recommendations` | GET | Personalized recommendations |

### Assessment & Results
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/results/mcq` | POST | Save MCQ results |
| `/leaderboard` | GET | View leaderboard |

### Utilities
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/upload` | POST | File upload |

## Request/Response Examples

### User Registration
```bash
POST /auth/register
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword",
  "role": "student",
  "section": "A"
}
```

### Generate MCQ Questions
```bash
POST /getQuestions
Content-Type: application/json

{
  "Topic": "Python Programming",
  "Type": "MCQ",
  "Quantity": "5",
  "Difficulty": "medium"
}
```

### Create Assignment
```bash
POST /teacher/assignments
Content-Type: application/json

{
  "title": "Data Structures Implementation",
  "description": "Implement linked lists and trees",
  "teacher_id": "teacher123",
  "subject": "Computer Science",
  "due_date": "2024-02-15",
  "target_sections": ["A", "B"],
  "max_grade": 100
}
```

### Save MCQ Results
```bash
POST /results/mcq
Content-Type: application/json

{
  "user_id": "student123",
  "user_name": "John Doe",
  "topic": "Python Basics",
  "difficulty": "medium",
  "score": "8",
  "total": "10",
  "duration_ms": "300000"
}
```

## Database Schema

### Collections

#### Users
```javascript
{
  "_id": ObjectId,
  "name": String,
  "email": String (unique),
  "password": String (hashed),
  "role": String, // "student" or "teacher"
  "section": String,
  "created_at": Date,
  "updated_at": Date,
  "last_login": Date,
  "is_active": Boolean
}
```

#### Assignments
```javascript
{
  "_id": ObjectId,
  "title": String,
  "description": String,
  "teacher_id": String,
  "subject": String,
  "due_date": String,
  "target_sections": [String],
  "target_students": [String],
  "is_global": Boolean,
  "max_grade": Number,
  "created_at": Date,
  "updated_at": Date,
  "status": String
}
```

#### Submissions
```javascript
{
  "_id": ObjectId,
  "student_id": String,
  "assignment_id": String,
  "content": String,
  "submitted_at": Date,
  "status": String,
  "grade": Number,
  "ai_feedback": Object,
  "teacher_feedback": String
}
```

#### Study Materials
```javascript
{
  "_id": ObjectId,
  "title": String,
  "subject": String,
  "type": String, // "pdf", "video", "url", etc.
  "description": String,
  "url": String,
  "teacher_id": String,
  "uploaded_at": Date,
  "views": Number,
  "downloads": Number,
  "tags": [String],
  "is_active": Boolean
}
```

## Testing

Run the comprehensive test suite:

```bash
python test_api.py
```

This will test all endpoints and provide detailed results.

## Security Features

- **Password Hashing**: PBKDF2 with salt
- **Input Validation**: Comprehensive request validation
- **File Security**: Secure file upload handling
- **Error Handling**: Detailed logging without exposing sensitive data
- **CORS Protection**: Configurable cross-origin policies

## Monitoring & Logging

- **Request Logging**: All API requests logged with details
- **Error Tracking**: Comprehensive error logging
- **Performance Metrics**: Response time tracking
- **Debug Information**: Detailed debug logs in `api_debug.log`

## AI Integration Details

### Gemini AI Features
- **Question Generation**: Contextual MCQ and coding problems
- **Code Evaluation**: Automated code assessment
- **Feedback Generation**: Personalized learning feedback
- **Recommendation Engine**: AI-driven study suggestions

### Fallback Mechanisms
- **Question Fallbacks**: Local question generation when AI unavailable
- **Error Handling**: Graceful degradation for AI services
- **Rate Limiting**: Built-in quota management

## Deployment

### Production Setup
1. **Environment Variables**
```env
FLASK_ENV=production
GEMINI_API_KEY=your_production_key
MONGO_URI=your_production_mongodb_uri
SECRET_KEY=your_secret_key
```

2. **Production Server**
```bash
# Using Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5003 app:app

# Using uWSGI
pip install uwsgi
uwsgi --http 0.0.0.0:5003 --module app:app
```

3. **Docker Deployment**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5003
CMD ["python", "app.py"]
```

## Performance Optimization

- **Database Indexing**: Optimized queries with proper indexes
- **Caching**: Request result caching for improved performance
- **Connection Pooling**: Efficient database connections
- **Async Processing**: Background task processing for heavy operations

## Contributing

1. Follow PEP 8 style guidelines
2. Add comprehensive tests for new features
3. Update documentation for API changes
4. Use proper error handling and logging

## Troubleshooting

### Common Issues

1. **MongoDB Connection Failed**
   - Check MongoDB is running
   - Verify MONGO_URI in environment
   - Check network connectivity

2. **Gemini API Quota Exceeded**
   - Check API key validity
   - Monitor usage limits
   - Implement fallback mechanisms

3. **Import Errors**
   - Verify all dependencies installed
   - Check Python version compatibility
   - Ensure virtual environment activated

4. **File Upload Issues**
   - Check file permissions
   - Verify upload directory exists
   - Monitor disk space

### Debug Mode
```bash
export FLASK_DEBUG=1
python app.py
```

## API Rate Limits

- **Default**: 100 requests/minute per IP
- **Authentication**: 1000 requests/minute for authenticated users
- **AI Endpoints**: 10 requests/minute (due to external API limits)

## Support

For technical support:
1. Check logs in `api_debug.log`
2. Run test suite: `python test_api.py`
3. Verify environment configuration
4. Check MongoDB connection and data

## Version History

- **v1.0**: Initial release with basic CRUD operations
- **v1.1**: Added AI integration with Gemini
- **v1.2**: Enhanced dashboard features
- **v1.3**: Comprehensive analytics and reporting
- **v2.0**: Full student/teacher dashboard integration
