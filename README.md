# EDULEARN - Educational Learning Platform

A comprehensive educational platform with AI-powered features, role-based access control, and advanced analytics.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ (for backend)
- Node.js 16+ (for frontend)
- MongoDB (or use the included mock database)

### Backend Setup

1. **Install Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Start Backend Server**
   ```bash
   # Option 1: Using Python
   python main.py
   
   # Option 2: Using batch file (Windows)
   start_backend.bat
   
   # Option 3: Using startup script
   python ../start_backend.py
   ```

   The backend will start on `http://127.0.0.1:5001`

### Frontend Setup

1. **Install Dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start Frontend Server**
   ```bash
   # Option 1: Using npm
   npm run dev
   
   # Option 2: Using batch file (Windows)
   start_frontend.bat
   ```

   The frontend will start on `http://localhost:5173`

## 🎯 Features

### Core Features
- **User Authentication**: Login, signup, role-based access
- **Assessment System**: Multiple choice and coding assessments
- **Coding Platform**: Integrated code editor with execution
- **Progress Tracking**: Detailed analytics and progress charts
- **Gamification**: Badges, streaks, and leaderboards

### Admin Dashboard
- **User Management**: Complete CRUD operations, bulk import/export
- **System Analytics**: Platform metrics, user engagement, content performance
- **Content Oversight**: Global content library and curation system
- **Teacher Performance**: Analytics for teacher effectiveness

### Teacher Dashboard
- **Batch Management**: Create and manage student batches
- **Assessment Creation**: Build custom assessments
- **Student Analytics**: Track student progress and performance
- **AI-Powered Features**: Smart assessments and student reports

### Student Dashboard
- **Personalized Learning**: AI-powered learning paths
- **Progress Tracking**: Visual progress charts and analytics
- **Notifications**: Real-time notifications for batch assignments
- **Gamification**: Achievements, badges, and streaks

## 🔧 API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/status` - Check authentication status

### Admin Endpoints
- `GET /api/admin/users` - Get all users
- `POST /api/admin/users` - Create user
- `PUT /api/admin/users/{id}` - Update user
- `DELETE /api/admin/users/{id}` - Delete user
- `GET /api/admin/analytics/platform` - Platform metrics
- `GET /api/admin/content/library` - Content library

### Teacher Endpoints
- `GET /api/teacher/batches` - Get teacher batches
- `POST /api/teacher/batches` - Create batch
- `POST /api/teacher/batches/{id}/students/{student_id}` - Add student to batch
- `GET /api/teacher/analytics/class` - Class analytics

### Student Endpoints
- `GET /api/notifications/` - Get notifications
- `POST /api/notifications/{id}/read` - Mark notification as read
- `GET /api/coding/problems` - Get coding problems
- `POST /api/coding/submit` - Submit coding solution

## 🏗️ Project Structure

```
EDULEARN/
├── backend/
│   ├── app/
│   │   ├── api/                 # API endpoints
│   │   ├── core/                # Core configuration
│   │   ├── db/                  # Database utilities
│   │   ├── models/              # Data models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Business logic
│   │   └── utils/               # Utility functions
│   ├── main.py                  # Backend entry point
│   └── requirements.txt         # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── pages/               # Page components
│   │   ├── services/            # API services
│   │   └── utils/               # Utility functions
│   └── package.json             # Node.js dependencies
├── start_backend.py             # Backend startup script
├── start_backend.bat            # Windows backend startup
├── start_frontend.bat           # Windows frontend startup
└── README.md                    # This file
```

## 🔐 Default Admin Account

- **Email**: `admin@modlrn.com`
- **Password**: `admin123`
- **Role**: Admin

## 🧪 Testing

### Backend Testing
```bash
cd backend
python -m pytest app/tests/
```

### Manual Testing
```bash
# Test backend health
curl http://127.0.0.1:5001/api/health

# Test admin authentication
curl -X POST http://127.0.0.1:5001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@modlrn.com", "password": "admin123"}'
```

## 🚀 Deployment

### Backend Deployment
1. Set environment variables
2. Configure database connection
3. Deploy using uvicorn or gunicorn

### Frontend Deployment
1. Build the project: `npm run build`
2. Deploy the `dist` folder to your hosting service

## 📝 Development

### Adding New Features
1. Create API endpoints in `backend/app/api/`
2. Add frontend components in `frontend/src/components/`
3. Update routing in `frontend/src/App.tsx`
4. Test thoroughly before deployment

### Database Schema
The project uses MongoDB with the following main collections:
- `users` - User accounts and profiles
- `assessments` - Assessment definitions
- `results` - Assessment results
- `batches` - Teacher batches
- `notifications` - User notifications
- `questions` - Question bank

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Check the documentation
- Review the API endpoints
- Test with the provided admin account
- Check the console for error messages

---

**Happy Learning! 🎓**