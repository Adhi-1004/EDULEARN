# 🎯 EDULEARN Platform - Complete Features Guide

## 📋 Table of Contents

1. [Introduction](#introduction)
2. [Feature Categories](#feature-categories)
3. [Quick Feature Reference](#quick-feature-reference)
4. [Detailed Feature Documentation](#detailed-feature-documentation)
5. [System Architecture Overview](#system-architecture-overview)
6. [Technology Stack](#technology-stack)

---

## Introduction

This comprehensive guide documents every feature in the EDULEARN platform, providing detailed explanations of how each feature works, the technical flow from frontend to backend, all involved files and endpoints, and visual diagrams to illustrate the complete request-response cycle.

**Target Audience:**
- New developers joining the project
- Technical stakeholders understanding system architecture
- Maintenance and debugging teams
- Future feature developers

**Documentation Structure:**
This guide is organized into multiple detailed documents:
- **AUTHENTICATION_FEATURES.md** - All authentication and user management features
- **ASSESSMENT_FEATURES.md** - Assessment creation, management, and submission
- **STUDENT_FEATURES.md** - Student-specific functionality and learning tools
- **TEACHER_FEATURES.md** - Teacher dashboard, batch management, and analytics
- **ADMIN_FEATURES.md** - Platform administration and system monitoring
- **CODING_PLATFORM_FEATURES.md** - Complete coding practice and evaluation system

---

## Feature Categories

### 🔐 1. Authentication & User Management
Complete user lifecycle management with multiple authentication methods.

**Features:**
- Email/Password Registration & Login
- Face Recognition Authentication
- Google OAuth Integration
- Session Management & JWT Tokens
- Password Reset
- User Profile Management
- Role-Based Access Control (Student/Teacher/Admin)

**📖 Detailed Documentation:** [AUTHENTICATION_FEATURES.md](./AUTHENTICATION_FEATURES.md)

---

### 📝 2. Assessment System
Comprehensive assessment creation, management, and evaluation system.

**Features:**
- **Teacher Features:**
  - Manual Assessment Creation
  - AI-Generated Assessment Creation
  - Coding Assessment Creation
  - Question Bank Management
  - Assessment Publishing
  - Batch Assignment
  - Result Analytics

- **Student Features:**
  - View Available Assessments
  - Take MCQ Assessments
  - Take Coding Assessments
  - View Results & Detailed Feedback
  - Leaderboard Access
  - Topic Preference Configuration

**📖 Detailed Documentation:** [ASSESSMENT_FEATURES.md](./ASSESSMENT_FEATURES.md)

---

### 👨‍🎓 3. Student Learning Platform
Personalized learning experience with gamification and progress tracking.

**Features:**
- Dashboard with Learning Analytics
- Assessment History & Performance Tracking
- Gamification System (XP, Levels, Badges, Streaks)
- Notification Center
- Topic Selection for Personalized Assessments
- Progress Visualization
- Achievement Tracking

**📖 Detailed Documentation:** [STUDENT_FEATURES.md](./STUDENT_FEATURES.md)

---

### 👨‍🏫 4. Teacher Management System
Complete classroom management and student monitoring tools.

**Features:**
- Teacher Dashboard with Analytics
- Batch Creation & Management
- Student Management (Individual & Bulk)
- Assessment Creation & Publishing
- Student Performance Analytics
- AI-Powered Student Reports
- Feedback System
- Upcoming Assessments Overview

**📖 Detailed Documentation:** [TEACHER_FEATURES.md](./TEACHER_FEATURES.md)

---

### 👑 5. Admin Control Panel
Platform-wide administration and monitoring capabilities.

**Features:**
- Platform Analytics & Statistics
- User Management (CRUD Operations)
- System Health Monitoring
- Bulk User Import/Export
- Content Oversight & Curation
- Teacher Performance Analytics
- Database Health Checks
- System Resource Monitoring

**📖 Detailed Documentation:** [ADMIN_FEATURES.md](./ADMIN_FEATURES.md)

---

### 💻 6. Coding Practice Platform
Interactive coding environment with AI-powered problem generation.

**Features:**
- AI-Powered Problem Generation (Google Gemini)
- Multi-Language Support (Python, JavaScript, Java, C++, etc.)
- Real-Time Code Execution (Judge0 Integration)
- Test Case Validation
- Solution Submission & Evaluation
- Coding Session Tracking
- Personal Analytics Dashboard
- AI-Powered Learning Path Recommendations
- Difficulty Progression System

**📖 Detailed Documentation:** [CODING_PLATFORM_FEATURES.md](./CODING_PLATFORM_FEATURES.md)

---

### 🔔 7. Notification System
Real-time notification delivery and management.

**Features:**
- Real-Time Notifications
- Assessment Notifications
- Achievement Notifications
- Notification Preferences
- Read/Unread Status Management
- Notification History

**📖 Detailed Documentation:** Covered in respective feature documents

---

## Quick Feature Reference

### Authentication Features

| Feature | User Roles | Key Endpoints | Frontend Pages |
|---------|-----------|---------------|----------------|
| Email/Password Login | All | `POST /auth/login` | `/login` |
| Email/Password Registration | All | `POST /auth/register` | `/register` |
| Face Recognition Login | All | `POST /auth/face` | `/face-login` |
| Google OAuth | All | `GET /auth/google` | `/login` |
| Logout | All | `POST /auth/logout` | All |
| Profile Management | All | `GET/PUT /users/me` | `/profile` |

### Student Features

| Feature | Key Endpoints | Frontend Pages | Primary Files |
|---------|---------------|----------------|---------------|
| View Available Assessments | `GET /assessments/student/available` | `/student/assessments` | `AssessmentList.tsx` |
| Take MCQ Assessment | `POST /assessments/{id}/submit` | `/assessment/{id}` | `TakeAssessment.tsx` |
| Take Coding Assessment | `POST /assessments/{id}/coding-submit` | `/coding-assessment/{id}` | `CodingAssessment.tsx` |
| View Results | `GET /results/user/{id}` | `/results` | `ResultsPage.tsx` |
| View Leaderboard | `GET /assessments/{id}/leaderboard` | `/leaderboard/{id}` | `Leaderboard.tsx` |
| Gamification Dashboard | `GET /users/{id}/gamification` | `/dashboard` | `StudentDashboard.tsx` |

### Teacher Features

| Feature | Key Endpoints | Frontend Pages | Primary Files |
|---------|---------------|----------------|---------------|
| Create Assessment | `POST /assessments/` | `/teacher/create-assessment` | `CreateAssessment.tsx` |
| Add Questions | `POST /assessments/{id}/questions` | `/teacher/assessment/{id}/edit` | `QuestionBuilder.tsx` |
| Generate AI Questions | `POST /assessments/{id}/ai-generate-questions` | `/teacher/assessment/{id}/generate` | `AIQuestionGenerator.tsx` |
| Publish Assessment | `POST /assessments/{id}/publish` | `/teacher/assessments` | `AssessmentManagement.tsx` |
| Create Batch | `POST /teacher/batches` | `/teacher/batches` | `BatchManagement.tsx` |
| Add Students | `POST /teacher/students/add` | `/teacher/batch/{id}/students` | `StudentManagement.tsx` |
| Bulk Upload Students | `POST /bulk-students/upload` | `/teacher/bulk-upload` | `BulkStudentUpload.tsx` |
| View Analytics | `GET /teacher/analytics/overview` | `/teacher/analytics` | `TeacherAnalytics.tsx` |
| Generate Student Report | `POST /teacher/generate-student-report` | `/teacher/student/{id}/report` | `StudentReport.tsx` |

### Admin Features

| Feature | Key Endpoints | Frontend Pages | Primary Files |
|---------|---------------|----------------|---------------|
| Platform Analytics | `GET /admin/analytics/platform` | `/admin/dashboard` | `AdminDashboard.tsx` |
| User Management | `GET/POST/PUT/DELETE /admin/users` | `/admin/users` | `UserManagement.tsx` |
| System Health | `GET /health/comprehensive` | `/admin/health` | `SystemHealth.tsx` |
| Bulk Import Users | `POST /admin/users/bulk-import` | `/admin/bulk-import` | `BulkImport.tsx` |
| Export Users | `GET /admin/users/export` | `/admin/users` | `UserManagement.tsx` |
| Content Oversight | `GET /admin/content/library` | `/admin/content` | `ContentOversight.tsx` |

### Coding Platform Features

| Feature | Key Endpoints | Frontend Pages | Primary Files |
|---------|---------------|----------------|---------------|
| Generate Problem | `POST /coding/problems/generate` | `/coding/practice` | `ProblemGenerator.tsx` |
| Get Problems | `GET /coding/problems` | `/coding/problems` | `ProblemList.tsx` |
| Execute Code | `POST /coding/execute` | `/coding/solve/{id}` | `CodeEditor.tsx` |
| Submit Solution | `POST /coding/submit` | `/coding/solve/{id}` | `CodeEditor.tsx` |
| Start Session | `POST /coding/sessions/start` | `/coding/solve/{id}` | `CodingSession.tsx` |
| View Analytics | `GET /coding/analytics` | `/coding/analytics` | `CodingAnalytics.tsx` |
| Generate Learning Path | `POST /coding/analytics/learning-path` | `/coding/learning-path` | `LearningPath.tsx` |

---

## System Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                        │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   Student    │  │   Teacher    │  │    Admin     │        │
│  │  Dashboard   │  │  Dashboard   │  │   Dashboard  │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │         API Services (authService, etc.)                │  │
│  └─────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP/HTTPS (Axios)
                             │
┌────────────────────────────┴────────────────────────────────────┐
│                    BACKEND (FastAPI)                            │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              API Routes & Authentication                 │  │
│  │  (JWT Middleware, Role-Based Access Control)            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   Auth API   │  │Assessment API│  │  Coding API  │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │ Teacher API  │  │  Admin API   │  │  Users API   │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                   ┌─────────┴─────────┐
                   │                   │
┌──────────────────┴─────┐   ┌─────────┴──────────────┐
│   MongoDB Database     │   │  External Services     │
│                        │   │                        │
│  - Users Collection    │   │  - Google OAuth        │
│  - Assessments         │   │  - Judge0 API          │
│  - Results             │   │  - Google Gemini AI    │
│  - Batches             │   │  - Face Recognition    │
│  - Coding Problems     │   │                        │
└────────────────────────┘   └────────────────────────┘
```

### Request Flow Pattern

All features in EDULEARN follow a similar architectural pattern:

```
┌─────────────┐         ┌──────────────┐        ┌─────────────┐
│  Frontend   │────────▶│   Backend    │───────▶│  Database   │
│  Component  │  HTTP   │   Endpoint   │ Query  │ (MongoDB)   │
│             │◀────────│              │◀───────│             │
└─────────────┘ Response└──────────────┘ Result └─────────────┘
      │                        │
      │                        │
      ▼                        ▼
┌─────────────┐         ┌──────────────┐
│   Service   │         │ Dependencies │
│   Layer     │         │ - Auth       │
│ (API calls) │         │ - Validation │
└─────────────┘         │ - AI/Judge0  │
                        └──────────────┘
```

### Authentication Flow

```
Every authenticated request follows this pattern:

1. Frontend stores JWT token (localStorage/cookie)
2. Frontend includes token in Authorization header
3. Backend validates token with get_current_user dependency
4. Backend checks user role for authorization
5. Request proceeds if authorized, otherwise 401/403 error
```

---

## Technology Stack

### Frontend
- **Framework:** React 18 with TypeScript
- **Routing:** React Router v6
- **HTTP Client:** Axios
- **State Management:** React Hooks + Context API
- **UI Components:** Custom components + Tailwind CSS
- **Code Editor:** Monaco Editor (for coding platform)
- **Face Recognition:** face-api.js

### Backend
- **Framework:** FastAPI (Python 3.11+)
- **Database:** MongoDB with Motor (async driver)
- **Authentication:** JWT (python-jose), OAuth2
- **Validation:** Pydantic v2
- **AI Integration:** Google Gemini AI API
- **Code Execution:** Judge0 API
- **Face Recognition:** face_recognition library

### Infrastructure
- **Database:** MongoDB Atlas (Cloud)
- **External APIs:**
  - Google OAuth 2.0
  - Judge0 Code Execution Engine
  - Google Gemini AI (Generative AI)
- **File Storage:** Local + Cloud options

### Development Tools
- **Package Managers:** npm (frontend), pip (backend)
- **Environment Management:** python-dotenv, .env files
- **API Documentation:** FastAPI automatic docs (Swagger/ReDoc)

---

## How to Use This Documentation

### For New Developers
1. Start with this overview to understand all available features
2. Read the [AUTHENTICATION_FEATURES.md](./AUTHENTICATION_FEATURES.md) to understand the security model
3. Pick the feature category you'll work on and read its detailed documentation
4. Reference [COMPLETE_API_REFERENCE.md](./COMPLETE_API_REFERENCE.md) for specific endpoint details

### For Feature Development
1. Identify the feature category
2. Review the existing flow diagrams in the relevant documentation
3. Check what endpoints and files are involved
4. Follow the established patterns when adding new features

### For Debugging
1. Use the flow diagrams to understand the request path
2. Check the file locations to find the relevant code
3. Review the request/response examples to verify data structures
4. Use the health check endpoints to verify system status

### For System Architecture
1. Review the architecture diagrams in this document
2. Understand the role-based access control model
3. Study the authentication flow that protects all endpoints
4. Review the database schema in each feature document

---

## Feature Implementation Patterns

All features in EDULEARN follow consistent patterns:

### 1. **Frontend Service Pattern**
```typescript
// Located in: frontend/src/api/{service}Service.ts
export const performAction = async (data: Type) => {
  const response = await api.post('/endpoint', data);
  return response.data;
};
```

### 2. **Backend Endpoint Pattern**
```python
# Located in: backend/app/api/{module}.py
@router.post("/endpoint")
async def endpoint_function(
    data: RequestModel,
    current_user: dict = Depends(get_current_user)
):
    # Validation
    # Business Logic
    # Database Operations
    # Response
    return ResponseModel(...)
```

### 3. **Authentication Pattern**
```python
# All protected endpoints use:
current_user: dict = Depends(get_current_user)

# Role-based access uses:
current_user: dict = Depends(require_role("teacher"))
```

### 4. **Database Operation Pattern**
```python
# Collection access
collection = database[db_name]["collection_name"]

# Insert
result = await collection.insert_one(document)

# Query
documents = await collection.find(filter).to_list(length=100)

# Update
await collection.update_one({"_id": id}, {"$set": update_data})
```

---

## Next Steps

Choose a feature category to explore in detail:

1. **[Authentication Features →](./AUTHENTICATION_FEATURES.md)**
   - Login, Registration, OAuth, Face Recognition

2. **[Assessment Features →](./ASSESSMENT_FEATURES.md)**
   - Assessment Creation, Management, Submission, Grading

3. **[Student Features →](./STUDENT_FEATURES.md)**
   - Learning Dashboard, Gamification, Progress Tracking

4. **[Teacher Features →](./TEACHER_FEATURES.md)**
   - Batch Management, Student Analytics, Report Generation

5. **[Admin Features →](./ADMIN_FEATURES.md)**
   - Platform Management, User Administration, System Monitoring

6. **[Coding Platform →](./CODING_PLATFORM_FEATURES.md)**
   - Problem Generation, Code Execution, Learning Paths

---

## Additional Resources

- **[Complete API Reference](./COMPLETE_API_REFERENCE.md)** - Detailed API endpoint documentation
- **[API Endpoints Summary](./API_ENDPOINTS_SUMMARY.md)** - Quick reference table
- **[README.md](../README.md)** - Project setup and installation guide

---

**Document Version:** 1.0  
**Last Updated:** October 2025  
**Maintained By:** EDULEARN Development Team

