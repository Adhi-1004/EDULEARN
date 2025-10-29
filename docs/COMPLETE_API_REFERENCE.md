# EDULEARN - Complete API Reference & Endpoint Mapping

## 📋 Table of Contents

1. [Overview](#overview)
2. [API Base URL](#api-base-url)
3. [Authentication](#authentication)
4. [Core API Endpoints](#core-api-endpoints)
   - [Authentication APIs](#authentication-apis)
   - [Assessment APIs](#assessment-apis)
   - [Coding Platform APIs](#coding-platform-apis)
   - [Teacher Management APIs](#teacher-management-apis)
   - [Admin Management APIs](#admin-management-apis)
   - [User Management APIs](#user-management-apis)
   - [Results & Analytics APIs](#results--analytics-apis)
   - [Notification APIs](#notification-apis)
   - [Bulk Operations APIs](#bulk-operations-apis)
   - [Health Check APIs](#health-check-apis)
   - [AI Question APIs](#ai-question-apis)
5. [Frontend-Backend Mapping](#frontend-backend-mapping)
6. [Authentication Flow](#authentication-flow)
7. [Error Handling](#error-handling)
8. [Best Practices](#best-practices)

---

## Overview

EDULEARN is a comprehensive educational platform with AI-powered assessment generation, coding practice, batch management, and gamification features. This document provides a complete reference for all API endpoints, their mappings between frontend and backend, and usage examples.

**Key Features:**
- 🔐 Multi-factor authentication (Email, Google OAuth, Face Recognition)
- 📝 AI-powered assessment generation using Gemini AI
- 💻 Coding practice platform with Judge0 integration
- 👥 Batch management for teachers
- 📊 Advanced analytics and gamification
- 🔔 Real-time notifications
- 📤 Bulk upload for students and teachers

---

## API Base URL

**Development:** `http://localhost:5001`
**Production:** `https://your-domain.com`

**API Prefix:** All API endpoints are prefixed with `/api` (except authentication endpoints which use `/auth`)

---

## Authentication

### Authentication Header
All authenticated requests must include the JWT token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

### Token Storage
- **Frontend:** Stored in `localStorage` as `access_token`
- **Expiry:** 30 minutes (configurable in backend settings)
- **Refresh:** No automatic refresh implemented (user must re-login)

---

## Core API Endpoints

### Authentication APIs

#### 1. User Registration
**Backend Endpoint:** `POST /auth/register`  
**Frontend Service:** `authService.register()`  
**File Locations:**
- Backend: `backend/app/api/auth.py` (Line 78-184)
- Frontend: `frontend/src/api/authService.ts` (Line 42-44)

**Request:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "role": "student|teacher|admin",
  "name": "string"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User registered successfully",
  "access_token": "jwt_token_here",
  "user": {
    "id": "string",
    "email": "string",
    "username": "string",
    "name": "string",
    "role": "string",
    "is_admin": false
  }
}
```

**Features:**
- Password hashing with bcrypt
- Automatic JWT token generation
- Role-based access setup
- Email validation

---

#### 2. User Login
**Backend Endpoint:** `POST /auth/login`  
**Frontend Service:** `authService.login()`  
**File Locations:**
- Backend: `backend/app/api/auth.py` (Line 186-233)
- Frontend: `frontend/src/api/authService.ts` (Line 34-36)

**Request:**
```json
{
  "email": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "access_token": "jwt_token_here",
  "user": {
    "id": "string",
    "email": "string",
    "username": "string",
    "role": "string",
    "is_admin": false
  }
}
```

---

#### 3. Face Recognition Login
**Backend Endpoint:** `POST /auth/face`  
**Frontend Service:** Custom implementation  
**File Locations:**
- Backend: `backend/app/api/auth.py` (Line 235-302)

**Request:**
```json
{
  "face_descriptor": [128 float values]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Face login successful",
  "access_token": "jwt_token_here",
  "user": {
    "id": "string",
    "email": "string",
    "username": "string"
  }
}
```

**Features:**
- Euclidean distance calculation for face matching
- Threshold-based verification (0.8)
- 128-dimensional face descriptor comparison

---

#### 4. Face Status Check
**Backend Endpoint:** `GET /auth/face-status`  
**Frontend Service:** Custom implementation  
**File Locations:**
- Backend: `backend/app/api/auth.py` (Line 304-328)

**Response:**
```json
{
  "success": true,
  "has_face": true
}
```

---

#### 5. Register Face
**Backend Endpoint:** `POST /auth/register-face`  
**Frontend Service:** Custom implementation  
**File Locations:**
- Backend: `backend/app/api/auth.py` (Line 330-361)

**Request:**
```json
{
  "face_descriptor": [128 float values]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Face registered successfully"
}
```

---

#### 6. Google OAuth Login
**Backend Endpoint:** `GET /auth/google`  
**Callback:** `GET /auth/google/callback`  
**File Locations:**
- Backend: `backend/app/api/auth.py` (Line 363-489)

**Flow:**
1. User clicks "Sign in with Google"
2. Redirected to Google OAuth consent page
3. Google redirects back to `/auth/google/callback`
4. Backend exchanges code for user info
5. Creates/updates user and generates JWT
6. Redirects to frontend with token

**Redirect URL:**
```
http://localhost:5173/login?token=<jwt_token>
```

---

#### 7. Logout
**Backend Endpoint:** `POST /auth/logout`  
**Frontend Service:** `authService.logout()`  
**File Locations:**
- Backend: `backend/app/api/auth.py` (Line 491-497)
- Frontend: `frontend/src/api/authService.ts` (Line 58-60)

**Response:**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

#### 8. Authentication Status
**Backend Endpoint:** `GET /auth/status`  
**Frontend Service:** `authService.getCurrentUser()`  
**File Locations:**
- Backend: `backend/app/api/auth.py` (Line 499-537)
- Frontend: `frontend/src/api/authService.ts` (Line 50-52)

**Response:**
```json
{
  "isAuthenticated": true,
  "user": {
    "id": "string",
    "email": "string",
    "name": "string",
    "profile_picture": "string",
    "role": "student|teacher|admin",
    "is_admin": false
  }
}
```

---

### Assessment APIs

#### 1. Create Assessment (Teacher)
**Backend Endpoint:** `POST /api/assessments/`  
**Frontend Service:** `assessmentService.createAssessment()`  
**File Locations:**
- Backend: `backend/app/api/assessments/core.py` (Line 20-94)
- Frontend: `frontend/src/api/assessmentService.ts` (Line 143-146)

**Request:**
```json
{
  "title": "string",
  "subject": "string",
  "difficulty": "easy|medium|hard",
  "description": "string",
  "time_limit": 30,
  "max_attempts": 1,
  "type": "mcq|coding|ai",
  "questions": [],
  "batches": ["batch_id_1", "batch_id_2"]
}
```

**Response:**
```json
{
  "id": "string",
  "title": "string",
  "subject": "string",
  "difficulty": "string",
  "question_count": 10,
  "status": "draft|active",
  "created_at": "2024-01-01T00:00:00"
}
```

---

#### 2. Get Teacher Assessments
**Backend Endpoint:** `GET /api/assessments/`  
**Frontend Service:** `assessmentService.getTeacherAssessments()`  
**File Locations:**
- Backend: `backend/app/api/assessments/core.py` (Line 99-181)
- Frontend: `frontend/src/api/assessmentService.ts` (Line 151-154)

**Response:**
```json
[
  {
    "id": "string",
    "title": "string",
    "subject": "string",
    "difficulty": "string",
    "question_count": 10,
    "status": "draft|active|published",
    "type": "mcq|coding",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00",
    "assigned_batches": ["batch_id_1"]
  }
]
```

**Note:** Combines results from both `assessments` and `teacher_assessments` collections

---

#### 3. Get Assessment Details
**Backend Endpoint:** `GET /api/assessments/{assessment_id}/details`  
**Frontend Service:** `assessmentService.getAssessmentDetails()`  
**File Locations:**
- Backend: `backend/app/api/assessments/core.py` (Line 183-253)
- Frontend: `frontend/src/api/assessmentService.ts` (Line 237-240)

**Response:**
```json
{
  "id": "string",
  "title": "string",
  "subject": "string",
  "difficulty": "string",
  "description": "string",
  "time_limit": 30,
  "max_attempts": 1,
  "question_count": 10,
  "questions": [
    {
      "question": "string",
      "options": ["A", "B", "C", "D"],
      "correct_answer": 0,
      "explanation": "string"
    }
  ],
  "assigned_batches": ["batch_id_1"],
  "created_by": "teacher_id",
  "created_at": "2024-01-01T00:00:00",
  "status": "active",
  "type": "mcq"
}
```

---

#### 4. Publish Assessment
**Backend Endpoint:** `POST /api/assessments/{assessment_id}/publish`  
**Frontend Service:** `assessmentService.publishAssessment()`  
**File Locations:**
- Backend: `backend/app/api/assessments/core.py` (Line 255-310)
- Frontend: `frontend/src/api/assessmentService.ts` (Line 197-200)

**Response:**
```json
{
  "success": true,
  "message": "Assessment published successfully"
}
```

**Side Effects:**
- Creates notifications for all students in assigned batches
- Changes assessment status to "active"
- Sets `is_active` to `true`

---

#### 5. Assign Assessment to Batches
**Backend Endpoint:** `POST /api/assessments/{assessment_id}/assign-batches`  
**Frontend Service:** `assessmentService.assignToBatches()`  
**File Locations:**
- Backend: `backend/app/api/assessments/core.py` (Line 312-406)
- Frontend: `frontend/src/api/assessmentService.ts` (Line 205-208)

**Request:**
```json
["batch_id_1", "batch_id_2", "batch_id_3"]
```

**Response:**
```json
{
  "success": true,
  "message": "Assessment assigned to 3 batch(es)",
  "batch_count": 3,
  "student_count": 45,
  "batches": [
    {
      "batch_id": "string",
      "batch_name": "string",
      "student_count": 15
    }
  ]
}
```

---

#### 6. Get Student Available Assessments
**Backend Endpoint:** `GET /api/assessments/student/available`  
**Frontend Service:** `assessmentService.getAvailableAssessments()`  
**File Locations:**
- Backend: `backend/app/api/assessments/submissions.py` (Line 27-129)
- Frontend: `frontend/src/api/assessmentService.ts` (Line 159-162)

**Response:**
```json
[
  {
    "id": "string",
    "assessment_id": "string",
    "student_id": "string",
    "student_name": "string",
    "student_email": "string",
    "score": 0,
    "percentage": 0.0,
    "time_taken": 0,
    "submitted_at": "2024-01-01T00:00:00",
    "total_questions": 10
  }
]
```

**Logic:**
- Gets student's batch
- Finds assessments assigned to that batch
- Filters out already submitted assessments
- Checks both `assessments` and `teacher_assessments` collections

---

#### 7. Get Student Upcoming Assessments
**Backend Endpoint:** `GET /api/assessments/student/upcoming`  
**Frontend Service:** Custom implementation  
**File Locations:**
- Backend: `backend/app/api/assessments/submissions.py` (Line 134-317)

**Response:**
```json
[
  {
    "id": "string",
    "title": "string",
    "subject": "string",
    "difficulty": "easy|medium|hard",
    "description": "string",
    "time_limit": 30,
    "question_count": 10,
    "type": "mcq|coding",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00",
    "teacher_name": "string"
  }
]
```

**Features:**
- Finds all batches containing the student
- Gets assessments assigned to those batches
- Filters out submitted assessments
- Enriches with teacher information

---

#### 8. Submit Assessment
**Backend Endpoint:** `POST /api/assessments/{assessment_id}/submit`  
**Frontend Service:** `assessmentService.submitAssessment()`  
**File Locations:**
- Backend: `backend/app/api/assessments/submissions.py` (Line 405-545)
- Frontend: `frontend/src/api/assessmentService.ts` (Line 221-224)

**Request:**
```json
{
  "answers": [0, 2, 1, 3, 0],
  "time_taken": 1200
}
```

**Response:**
```json
{
  "id": "string",
  "assessment_id": "string",
  "student_id": "string",
  "student_name": "string",
  "score": 8.0,
  "total_questions": 10,
  "percentage": 80.0,
  "time_taken": 1200,
  "submitted_at": "2024-01-01T00:00:00",
  "attempt_number": 1
}
```

**Features:**
- Calculates score by comparing user answers with correct answers
- Updates user gamification progress (XP, level, streak, badges)
- Creates completion notification
- Stores submission in `assessment_submissions` or `teacher_assessment_results`

---

#### 9. Get Assessment Leaderboard
**Backend Endpoint:** `GET /api/assessments/{assessment_id}/leaderboard`  
**Frontend Service:** `assessmentService.getAssessmentLeaderboard()`  
**File Locations:**
- Backend: `backend/app/api/assessments/submissions.py` (Line 642-723)
- Frontend: `frontend/src/api/assessmentService.ts` (Line 245-248)

**Response:**
```json
{
  "assessment_id": "string",
  "assessment_title": "string",
  "total_students": 25,
  "leaderboard": [
    {
      "student_id": "string",
      "student_name": "string",
      "score": 10,
      "percentage": 100.0,
      "time_taken": 900,
      "rank": 1
    }
  ]
}
```

**Sorting Logic:**
- Primary: Percentage (descending)
- Secondary: Time taken (ascending)
- Handles ties correctly

---

### Coding Platform APIs

#### 1. Generate Coding Problem
**Backend Endpoint:** `POST /api/coding/problems/generate`  
**Frontend Service:** `codingService.generateProblem()`  
**File Locations:**
- Backend: `backend/app/api/coding.py` (Line 30-119)
- Frontend: `frontend/src/api/codingService.ts` (Line 164-175)

**Request:**
```json
{
  "topic": "Arrays",
  "difficulty": "easy|medium|hard",
  "user_skill_level": "beginner|intermediate|advanced",
  "focus_areas": ["Arrays", "Sorting"],
  "avoid_topics": ["Graphs"],
  "timestamp": 1234567890,
  "session_id": "string"
}
```

**Response:**
```json
{
  "success": true,
  "problem": {
    "id": "string",
    "title": "string",
    "description": "string",
    "topic": "string",
    "difficulty": "string",
    "constraints": ["constraint1", "constraint2"],
    "examples": [
      {
        "input": "string",
        "output": "string",
        "explanation": "string"
      }
    ],
    "test_cases": [
      {
        "input": "string",
        "output": "string"
      }
    ],
    "hints": ["hint1", "hint2"],
    "tags": ["tag1", "tag2"],
    "expected_complexity": {
      "time": "O(n)",
      "space": "O(1)"
    },
    "success_rate": 0.0,
    "average_time": null
  }
}
```

**Features:**
- Uses Gemini AI to generate unique problems
- Includes visible and hidden test cases
- Personalizes based on user skill level
- Supports timestamp and session_id for uniqueness

---

#### 2. Get Coding Problems
**Backend Endpoint:** `GET /api/coding/problems`  
**Frontend Service:** `codingService.getProblems()`  
**File Locations:**
- Backend: `backend/app/api/coding.py` (Line 121-178)
- Frontend: `frontend/src/api/codingService.ts` (Line 180-188)

**Query Parameters:**
- `topic`: Filter by topic (optional)
- `difficulty`: Filter by difficulty (optional)
- `limit`: Max results (1-100, default 20)
- `skip`: Pagination offset (default 0)

**Response:**
```json
{
  "success": true,
  "problems": [
    {
      "id": "string",
      "title": "string",
      "description": "string",
      "topic": "string",
      "difficulty": "string",
      "success_rate": 0.75,
      "average_time": 1200
    }
  ],
  "total": 50
}
```

---

#### 3. Get Coding Problem by ID
**Backend Endpoint:** `GET /api/coding/problems/{problem_id}`  
**Frontend Service:** `codingService.getProblem()`  
**File Locations:**
- Backend: `backend/app/api/coding.py` (Line 180-245)
- Frontend: `frontend/src/api/codingService.ts` (Line 193-196)

**Response:**
```json
{
  "success": true,
  "problem": {
    "id": "string",
    "title": "string",
    "description": "string",
    "topic": "string",
    "difficulty": "string",
    "constraints": [],
    "examples": [],
    "test_cases": [],
    "hints": [],
    "tags": [],
    "expected_complexity": {
      "time": "O(n)",
      "space": "O(1)"
    },
    "success_rate": 0.75,
    "average_time": 1200,
    "last_attempt": {
      "status": "accepted",
      "submitted_at": "2024-01-01T00:00:00",
      "execution_time": 150,
      "attempts": 3
    }
  }
}
```

---

#### 4. Execute Code
**Backend Endpoint:** `POST /api/coding/execute`  
**Frontend Service:** `codingService.executeCode()`  
**File Locations:**
- Backend: `backend/app/api/coding.py` (Line 249-287)
- Frontend: `frontend/src/api/codingService.ts` (Line 201-204)

**Request:**
```json
{
  "code": "def solution(nums):\n    return sum(nums)",
  "language": "python",
  "test_cases": [
    {
      "input": "[1, 2, 3]",
      "output": "6"
    }
  ],
  "time_limit": 5,
  "memory_limit": 256
}
```

**Response:**
```json
{
  "success": true,
  "execution_result": {
    "success": true,
    "execution_time": 150,
    "memory_used": 32,
    "results": [
      {
        "test_case_index": 0,
        "passed": true,
        "output": "6",
        "expected": "6",
        "test_input": "[1, 2, 3]",
        "execution_time": 150,
        "memory": 32
      }
    ],
    "output": "6",
    "error": null
  }
}
```

**Features:**
- Uses Judge0 API for code execution
- Supports multiple programming languages
- Returns detailed execution metrics
- Safe sandboxed execution

---

#### 5. Submit Coding Solution
**Backend Endpoint:** `POST /api/coding/submit`  
**Frontend Service:** `codingService.submitSolution()`  
**File Locations:**
- Backend: `backend/app/api/coding.py` (Line 379-522)
- Frontend: `frontend/src/api/codingService.ts` (Line 209-212)

**Request:**
```json
{
  "problem_id": "string",
  "code": "def solution(nums):\n    return sum(nums)",
  "language": "python"
}
```

**Response:**
```json
{
  "success": true,
  "submission": {
    "id": "string",
    "status": "accepted|wrong_answer|time_limit_exceeded|runtime_error",
    "execution_time": 150,
    "memory_used": 32,
    "test_results": [
      {
        "passed": true,
        "output": "6",
        "error": null
      }
    ],
    "submitted_at": "2024-01-01T00:00:00"
  }
}
```

**Features:**
- Runs against all test cases (visible + hidden)
- Updates user analytics and problem stats
- Awards XP based on difficulty
- Generates AI feedback asynchronously

---

#### 6. Get Coding Analytics
**Backend Endpoint:** `GET /api/coding/analytics`  
**Frontend Service:** `codingService.getAnalytics()`  
**File Locations:**
- Backend: `backend/app/api/coding.py` (Line 730-813)
- Frontend: `frontend/src/api/codingService.ts` (Line 249-252)

**Response:**
```json
{
  "success": true,
  "analytics": {
    "total_problems_solved": 25,
    "total_problems_attempted": 30,
    "success_rate": 83.3,
    "average_time_per_problem": 1200.5,
    "preferred_language": "python",
    "skill_level": "intermediate",
    "strong_topics": ["Arrays", "Strings"],
    "weak_topics": ["Graphs", "Dynamic Programming"],
    "improvement_areas": ["Time Complexity", "Edge Cases"],
    "learning_path": ["Practice Arrays", "Learn DP"],
    "coding_streak": 5,
    "longest_streak": 15,
    "problems_by_difficulty": {
      "easy": 10,
      "medium": 12,
      "hard": 3
    },
    "problems_by_topic": {
      "Arrays": 8,
      "Strings": 7,
      "Graphs": 3
    },
    "recent_activity": [
      {
        "problem_id": "string",
        "status": "accepted",
        "language": "python",
        "submitted_at": "2024-01-01T00:00:00",
        "execution_time": 150
      }
    ]
  }
}
```

---

#### 7. Generate Learning Path
**Backend Endpoint:** `POST /api/coding/analytics/learning-path`  
**Frontend Service:** `codingService.generateLearningPath()`  
**File Locations:**
- Backend: `backend/app/api/coding.py` (Line 815-883)
- Frontend: `frontend/src/api/codingService.ts` (Line 257-260)

**Response:**
```json
{
  "success": true,
  "learning_path": {
    "current_skill_assessment": {
      "level": "intermediate",
      "strengths": ["Arrays", "Strings"],
      "weaknesses": ["Graphs", "DP"],
      "confidence_score": 0.75
    },
    "learning_objectives": [
      {
        "goal": "Master Dynamic Programming",
        "priority": "high",
        "estimated_weeks": 4,
        "success_criteria": ["Solve 20 DP problems", "80% success rate"]
      }
    ],
    "recommended_topics": [
      {
        "topic": "Dynamic Programming",
        "difficulty": "medium",
        "problems_count": 20,
        "estimated_time": "4 weeks",
        "prerequisites": ["Arrays", "Recursion"],
        "learning_resources": ["DP Tutorial", "Practice Problems"]
      }
    ],
    "practice_schedule": {
      "daily_problems": 2,
      "weekly_goals": "Solve 14 problems",
      "review_schedule": "Every Sunday",
      "difficulty_progression": "Easy → Medium → Hard"
    },
    "improvement_areas": [
      {
        "area": "Time Complexity Analysis",
        "current_level": "basic",
        "target_level": "intermediate",
        "action_plan": ["Study Big-O notation", "Practice analysis"]
      }
    ],
    "milestone_tracking": [
      {
        "milestone": "Complete 10 DP problems",
        "target_date": "2024-02-01",
        "progress_indicators": ["Problems solved: 3/10"]
      }
    ]
  }
}
```

**Features:**
- AI-generated personalized learning path
- Based on user's solution history and analytics
- Includes specific goals and timelines
- Tracks milestones and progress

---

#### 8. Start Coding Session
**Backend Endpoint:** `POST /api/coding/sessions/start`  
**Frontend Service:** `codingService.startSession()`  
**File Locations:**
- Backend: `backend/app/api/coding.py` (Line 585-627)
- Frontend: `frontend/src/api/codingService.ts` (Line 225-228)

**Request:**
```json
{
  "problem_id": "string",
  "language": "python"
}
```

**Response:**
```json
{
  "success": true,
  "session_id": "string"
}
```

---

#### 9. Update Coding Session
**Backend Endpoint:** `PUT /api/coding/sessions/{session_id}`  
**Frontend Service:** `codingService.updateSession()`  
**File Locations:**
- Backend: `backend/app/api/coding.py` (Line 629-670)
- Frontend: `frontend/src/api/codingService.ts` (Line 233-236)

**Request:**
```json
{
  "keystrokes": 250,
  "lines_of_code": 15,
  "compilation_attempts": 2,
  "test_runs": 3,
  "hints_used": 1
}
```

**Response:**
```json
{
  "success": true
}
```

---

#### 10. End Coding Session
**Backend Endpoint:** `POST /api/coding/sessions/{session_id}/end`  
**Frontend Service:** `codingService.endSession()`  
**File Locations:**
- Backend: `backend/app/api/coding.py` (Line 672-727)
- Frontend: `frontend/src/api/codingService.ts` (Line 241-244)

**Request Body:**
```json
{
  "final_status": "accepted|wrong_answer|abandoned"
}
```

**Response:**
```json
{
  "success": true,
  "session_summary": {
    "total_time": 1800,
    "keystrokes": 250,
    "lines_of_code": 15,
    "compilation_attempts": 2,
    "test_runs": 3,
    "hints_used": 1,
    "final_status": "accepted"
  }
}
```

---

### Teacher Management APIs

#### 1. Get Teacher Dashboard
**Backend Endpoint:** `GET /api/teacher/dashboard`  
**File Locations:**
- Backend: `backend/app/api/teacher.py` (Line 65-111)

**Response:**
```json
{
  "teacher_id": "string",
  "total_students": 45,
  "active_batches": 3,
  "pending_assignments": 5,
  "recent_activities": [
    {
      "type": "assignment_submitted",
      "student_name": "John Doe",
      "assignment": "Math Quiz 1",
      "timestamp": "2024-01-01T00:00:00"
    }
  ],
  "performance_metrics": {
    "average_student_score": 85.5,
    "completion_rate": 78.2,
    "engagement_score": 82.1
  }
}
```

---

#### 2. Get Teacher Batches
**Backend Endpoint:** `GET /api/teacher/batches`  
**File Locations:**
- Backend: `backend/app/api/teacher.py` (Line 113-160)

**Response:**
```json
[
  {
    "id": "string",
    "name": "Batch A",
    "student_count": 15,
    "created_at": "2024-01-01T00:00:00",
    "status": "active",
    "description": "Morning batch"
  }
]
```

---

#### 3. Get Students (Filtered by Batch)
**Backend Endpoint:** `GET /api/teacher/students?batch_id={batch_id}`  
**File Locations:**
- Backend: `backend/app/api/teacher.py` (Line 162-224)

**Query Parameters:**
- `batch_id`: Filter by batch (optional, use "all" for all students)

**Response:**
```json
{
  "success": true,
  "students": [
    {
      "id": "string",
      "name": "John Doe",
      "email": "john@example.com",
      "progress": 75.5,
      "lastActive": "2024-01-01T00:00:00",
      "batch": "Batch A",
      "batchId": "string"
    }
  ]
}
```

---

#### 4. Create Batch
**Backend Endpoint:** `POST /api/teacher/batches`  
**File Locations:**
- Backend: `backend/app/api/teacher.py` (Line 423-465)

**Request:**
```json
{
  "name": "Batch A",
  "description": "Morning batch"
}
```

**Response:**
```json
{
  "success": true,
  "batch_id": "string",
  "message": "Batch 'Batch A' created successfully"
}
```

---

#### 5. Delete Batch
**Backend Endpoint:** `DELETE /api/teacher/batches/{batch_id}`  
**File Locations:**
- Backend: `backend/app/api/teacher.py` (Line 470-507)

**Response:**
```json
{
  "success": true,
  "message": "Batch deleted successfully",
  "batch_id": "string"
}
```

**Side Effects:**
- Removes batch references from all students
- Unassigns all assessments from this batch

---

#### 6. Add Student to Batch
**Backend Endpoint:** `POST /api/teacher/students/add`  
**File Locations:**
- Backend: `backend/app/api/teacher.py` (Line 528-672)

**Request:**
```json
{
  "email": "student@example.com",
  "name": "John Doe",
  "batch_id": "string"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Student added to batch 'Batch A'",
  "student_id": "string"
}
```

**Features:**
- Creates new student if doesn't exist
- Generates temporary password for new students
- Creates notification for student
- Adds student to batch's student_ids array

---

#### 7. Remove Student from Batch
**Backend Endpoint:** `POST /api/teacher/students/remove`  
**File Locations:**
- Backend: `backend/app/api/teacher.py` (Line 674-788)

**Request:**
```json
{
  "student_id": "string",
  "batch_id": "string"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Student removed from batch 'Batch A'"
}
```

**Features:**
- Removes batch references from student
- Removes student from batch's student_ids
- Creates removal notification

---

#### 8. Get Teacher Assessments
**Backend Endpoint:** `GET /api/teacher/assessments`  
**File Locations:**
- Backend: `backend/app/api/teacher.py` (Line 959-1015)

**Response:**
```json
[
  {
    "id": "string",
    "title": "Math Quiz",
    "topic": "Algebra",
    "subject": "Mathematics",
    "difficulty": "medium",
    "question_count": 10,
    "batches": ["batch_id_1"],
    "status": "published",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00",
    "submission_count": 25,
    "time_limit": 30,
    "description": "Algebra basics",
    "type": "teacher"
  }
]
```

**Note:** Fetches from `teacher_assessments` collection only

---

#### 9. Create Teacher Assessment
**Backend Endpoint:** `POST /api/teacher/assessments/create`  
**File Locations:**
- Backend: `backend/app/api/teacher.py` (Line 1017-1171)

**Request:**
```json
{
  "title": "Math Quiz",
  "topic": "Algebra",
  "difficulty": "medium",
  "question_count": 10,
  "batches": ["batch_id_1", "batch_id_2"],
  "type": "ai_generated|ai_coding|mcq",
  "description": "Algebra basics",
  "questions": [],
  "time_limit": 30
}
```

**Response:**
```json
{
  "success": true,
  "assessment_id": "string",
  "message": "Assessment 'Math Quiz' created successfully with 10 questions"
}
```

**Features:**
- Supports three types: `ai_generated` (MCQ), `ai_coding`, and `mcq` (manual)
- Auto-generates questions using Gemini AI for AI types
- Creates notifications for all students in selected batches
- Stores in `teacher_assessments` collection

---

#### 10. Generate AI Student Report
**Backend Endpoint:** `POST /api/teacher/generate-student-report`  
**File Locations:**
- Backend: `backend/app/api/teacher.py` (Line 894-939)

**Request:**
```json
{
  "studentId": "string",
  "teacherId": "string"
}
```

**Response:**
```json
{
  "success": true,
  "report": {
    "id": "string",
    "studentId": "string",
    "studentName": "John Doe",
    "generatedAt": "2024-01-01T00:00:00",
    "summary": "John Doe is showing consistent progress...",
    "strengths": ["Problem Solving", "Consistency"],
    "weaknesses": ["Time Management"],
    "recommendations": ["Practice timed quizzes", "Review mistakes"],
    "performanceTrend": "improving",
    "nextSteps": ["Complete 3 practice sets", "Review key concepts"]
  }
}
```

---

#### 11. Get AI Reports for Teacher
**Backend Endpoint:** `GET /api/teacher/ai-reports/{teacher_id}`  
**File Locations:**
- Backend: `backend/app/api/teacher.py` (Line 866-891)

**Response:**
```json
[
  {
    "id": "string",
    "studentId": "string",
    "studentName": "John Doe",
    "generatedAt": "2024-01-01T00:00:00",
    "summary": "Consistent progress...",
    "strengths": ["Problem Solving"],
    "weaknesses": ["Time Management"],
    "recommendations": ["Practice more"],
    "performanceTrend": "improving",
    "nextSteps": ["Complete practice sets"]
  }
]
```

---

### Admin Management APIs

#### 1. Get Platform Statistics
**Backend Endpoint:** `GET /api/admin/analytics/platform`  
**Alternate:** `GET /api/admin/stats/platform`  
**File Locations:**
- Backend: `backend/app/api/admin.py` (Line 47-108)

**Response:**
```json
{
  "total_users": 500,
  "active_users_today": 45,
  "active_users_week": 120,
  "total_teachers": 20,
  "total_students": 470,
  "total_assessments": 50,
  "platform_health_score": 95,
  "user_engagement_rate": 24.0,
  "pending_reviews": 3,
  "system_alerts": 1
}
```

---

#### 2. Get User Activity
**Backend Endpoint:** `GET /api/admin/users/activity?limit={limit}`  
**File Locations:**
- Backend: `backend/app/api/admin.py` (Line 110-151)

**Query Parameters:**
- `limit`: Max results (1-100, default 50)

**Response:**
```json
[
  {
    "user_id": "string",
    "username": "john_doe",
    "last_login": "2024-01-01T00:00:00",
    "activity_score": 0.8,
    "recent_actions": []
  }
]
```

---

#### 3. Get System Health
**Backend Endpoint:** `GET /api/admin/system/health`  
**File Locations:**
- Backend: `backend/app/api/admin.py` (Line 153-189)

**Response:**
```json
{
  "database_status": "healthy",
  "api_status": "healthy",
  "services_status": {
    "database": "healthy",
    "api": "healthy",
    "authentication": "healthy",
    "file_storage": "healthy"
  },
  "uptime": "24h",
  "version": "1.0.0"
}
```

---

#### 4. Bulk Import Users
**Backend Endpoint:** `POST /api/admin/users/bulk-import`  
**File Locations:**
- Backend: `backend/app/api/admin.py` (Line 191-253)

**Request:** Multipart form with CSV file

**Response:**
```json
{
  "message": "Bulk import completed",
  "imported_count": 50,
  "errors": [
    "User with email john@example.com already exists"
  ]
}
```

---

#### 5. Export Users
**Backend Endpoint:** `GET /api/admin/users/export?format={csv|json}`  
**File Locations:**
- Backend: `backend/app/api/admin.py` (Line 255-296)

**Query Parameters:**
- `format`: Export format (csv or json)

**Response (CSV):**
```json
{
  "content": "username,email,role,created_at\n...",
  "filename": "users_export_20240101_120000.csv",
  "content_type": "text/csv"
}
```

---

#### 6. Reset User Password
**Backend Endpoint:** `POST /api/admin/users/{user_id}/reset-password`  
**File Locations:**
- Backend: `backend/app/api/admin.py` (Line 298-335)

**Response:**
```json
{
  "message": "Password reset successfully",
  "temporary_password": "temp_password_123"
}
```

---

#### 7. Get All Users (Paginated)
**Backend Endpoint:** `GET /api/admin/users?page={page}&limit={limit}&role={role}`  
**File Locations:**
- Backend: `backend/app/api/admin.py` (Line 338-387)

**Query Parameters:**
- `page`: Page number (default 1)
- `limit`: Results per page (1-100, default 20)
- `role`: Filter by role (optional)

**Response:**
```json
{
  "users": [
    {
      "id": "string",
      "username": "john_doe",
      "email": "john@example.com",
      "role": "student",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00",
      "last_login": "2024-01-01T00:00:00"
    }
  ],
  "total": 500,
  "page": 1,
  "limit": 20,
  "total_pages": 25
}
```

---

#### 8. Get User Details with Analytics
**Backend Endpoint:** `GET /api/admin/users/{user_id}/details`  
**File Locations:**
- Backend: `backend/app/api/admin.py` (Line 520-598)

**Response:**
```json
{
  "user": {
    "id": "string",
    "name": "John Doe",
    "email": "john@example.com",
    "role": "student",
    "created_at": "2024-01-01T00:00:00",
    "last_login": "2024-01-01T12:00:00",
    "is_active": true
  },
  "analytics": {
    "id": "string",
    "name": "John Doe",
    "email": "john@example.com",
    "role": "student",
    "last_login": "2024-01-01T12:00:00",
    "total_logins": 45,
    "activity_score": 75.0,
    "progress_percentage": 60.0,
    "assessments_taken": 10,
    "average_score": 85.5,
    "badges_earned": 5,
    "streak_days": 7
  },
  "recent_activity": [
    {
      "action": "Completed Assessment",
      "timestamp": "2024-01-01T10:30:00"
    }
  ],
  "assessment_history": [],
  "badges": [
    {
      "name": "First Assessment",
      "earned_at": "2024-01-01T14:30:00"
    }
  ]
}
```

---

#### 9. Create User (Admin)
**Backend Endpoint:** `POST /api/admin/users`  
**File Locations:**
- Backend: `backend/app/api/admin.py` (Line 600-642)

**Request:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "name": "John Doe",
  "role": "student|teacher|admin"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User created successfully",
  "user_id": "string"
}
```

---

#### 10. Update User (Admin)
**Backend Endpoint:** `PUT /api/admin/users/{user_id}`  
**File Locations:**
- Backend: `backend/app/api/admin.py` (Line 644-688)

**Request:**
```json
{
  "username": "john_doe_updated",
  "email": "john.new@example.com",
  "name": "John Doe Jr.",
  "role": "student"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User updated successfully"
}
```

---

#### 11. Delete User (Admin)
**Backend Endpoint:** `DELETE /api/admin/users/{user_id}`  
**File Locations:**
- Backend: `backend/app/api/admin.py` (Line 690-729)

**Response:**
```json
{
  "success": true,
  "message": "User deleted successfully"
}
```

**Note:** Prevents deletion of admin users

---

#### 12. Get Content Analytics
**Backend Endpoint:** `GET /api/admin/analytics/content`  
**File Locations:**
- Backend: `backend/app/api/admin.py` (Line 732-792)

**Response:**
```json
{
  "total_content": 75,
  "content_analytics": [
    {
      "content_id": "1",
      "title": "Python Basics Assessment",
      "type": "assessment",
      "creator": "System",
      "views": 150,
      "completions": 120,
      "average_score": 78.5,
      "popularity_score": 85.2,
      "difficulty_rating": 3.2,
      "last_updated": "2024-01-15T10:30:00"
    }
  ],
  "timestamp": "2024-01-01T00:00:00"
}
```

---

#### 13. Get Teacher Performance Analytics
**Backend Endpoint:** `GET /api/admin/analytics/teachers`  
**File Locations:**
- Backend: `backend/app/api/admin.py` (Line 794-850)

**Response:**
```json
{
  "total_teachers": 20,
  "teacher_performance": [
    {
      "teacher_id": "string",
      "name": "Jane Smith",
      "email": "jane@example.com",
      "total_batches": 3,
      "total_students": 45,
      "total_completions": 150,
      "performance_score": 95.0,
      "engagement_rate": 78.5,
      "last_active": "2024-01-01T12:00:00",
      "created_at": "2024-01-01T00:00:00"
    }
  ],
  "timestamp": "2024-01-01T00:00:00"
}
```

---

### User Management APIs

#### 1. Get Current User Profile
**Backend Endpoint:** `GET /api/users/me`  
**File Locations:**
- Backend: `backend/app/api/users.py` (Line 101-126)

**Response:**
```json
{
  "user": {
    "id": "string",
    "username": "john_doe",
    "email": "john@example.com",
    "name": "John Doe",
    "role": "student",
    "is_admin": false
  },
  "stats": {
    "total_assignments": 10,
    "completed_assignments": 8,
    "average_score": 85.5
  }
}
```

---

#### 2. Update Current User Profile
**Backend Endpoint:** `PUT /api/users/me`  
**File Locations:**
- Backend: `backend/app/api/users.py` (Line 128-156)

**Request:**
```json
{
  "username": "john_doe_updated",
  "email": "john.new@example.com",
  "name": "John Doe Jr."
}
```

**Response:**
```json
{
  "id": "string",
  "username": "john_doe_updated",
  "email": "john.new@example.com",
  "name": "John Doe Jr.",
  "role": "student"
}
```

---

#### 3. Get User Gamification Data
**Backend Endpoint:** `GET /api/users/{user_id}/gamification`  
**File Locations:**
- Backend: `backend/app/api/users.py` (Line 301-356)

**Response:**
```json
{
  "xp": 1250,
  "level": 12,
  "streak": 7,
  "longest_streak": 15,
  "badges": ["first_assessment", "high_scorer", "consistent_learner"],
  "achievements": ["completed_10_assessments", "perfect_score"],
  "next_level_xp": 1300,
  "progress_to_next_level": 0.96
}
```

**Calculation:**
- Level = (XP ÷ 100) + 1
- Next Level XP = Current Level × 100
- Progress = (XP - Previous Level XP) ÷ 100

---

#### 4. Get User Badges
**Backend Endpoint:** `GET /api/users/{user_id}/badges`  
**File Locations:**
- Backend: `backend/app/api/users.py` (Line 358-412)

**Response:**
```json
[
  {
    "id": "first_login",
    "name": "Welcome",
    "description": "First login",
    "icon": "🎉",
    "earned": true,
    "earned_at": "2024-01-01T00:00:00"
  },
  {
    "id": "perfect_score",
    "name": "Perfectionist",
    "description": "Got 100% on a test",
    "icon": "💯",
    "earned": false,
    "earned_at": null
  }
]
```

**Available Badges:**
- `first_login` - Welcome
- `first_test` - Test Taker
- `perfect_score` - Perfectionist
- `streak_7` - Week Warrior
- `streak_30` - Month Master
- `coding_expert` - Code Master

---

### Results & Analytics APIs

#### 1. Get User Results
**Backend Endpoint:** `GET /api/results/user/{user_id}`  
**File Locations:**
- Backend: `backend/app/api/results.py` (Line 124-287)

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "id": "string",
      "test_name": "Math Quiz",
      "score": 8.0,
      "total_questions": 10,
      "correct_answers": 8,
      "completed_at": "2024-01-01T00:00:00",
      "duration": 1200,
      "topic": "Algebra",
      "difficulty": "medium",
      "percentage": 80.0,
      "time_taken": 1200,
      "date": "2024-01-01T00:00:00"
    }
  ],
  "total": 15
}
```

**Features:**
- Combines results from multiple collections:
  - `results` - General test results
  - `assessment_results` - Legacy results
  - `assessment_submissions` - Current regular assessments
  - `teacher_assessment_results` - Teacher-assigned assessments
- Sorted by completion date (most recent first)

---

#### 2. Get User Analytics
**Backend Endpoint:** `GET /api/results/analytics/{user_id}`  
**File Locations:**
- Backend: `backend/app/api/results.py` (Line 289-352)

**Response:**
```json
{
  "success": true,
  "analytics": {
    "total_assessments": 15,
    "total_questions": 150,
    "average_score": 85.5,
    "streak_days": 7,
    "topics": ["Mathematics", "Science", "Programming"],
    "recent_performance": [
      {
        "date": "2024-01-01",
        "score": 85.0
      }
    ]
  }
}
```

---

#### 3. Submit Assessment Result
**Backend Endpoint:** `POST /api/results/`  
**File Locations:**
- Backend: `backend/app/api/results.py` (Line 376-452)

**Request:**
```json
{
  "user_id": "string",
  "score": 8.0,
  "total_questions": 10,
  "questions": [],
  "user_answers": ["A", "B", "C"],
  "topic": "Algebra",
  "difficulty": "medium",
  "time_taken": 1200,
  "test_name": "Math Quiz"
}
```

**Response:**
```json
{
  "success": true,
  "score": 80.0,
  "correct_answers": 8,
  "total_questions": 10,
  "message": "Assessment completed! Score: 80.0%"
}
```

**Features:**
- Calculates score from user answers
- Updates user gamification progress
- Awards XP and badges
- Updates streak tracking

---

#### 4. Get Detailed Result
**Backend Endpoint:** `GET /api/results/{result_id}/detailed`  
**File Locations:**
- Backend: `backend/app/api/results.py` (Line 454-621)

**Response:**
```json
{
  "success": true,
  "result": {
    "id": "string",
    "user_id": "string",
    "score": 8,
    "total_questions": 10,
    "questions": [],
    "user_answers": ["A", "B", "C"],
    "topic": "Algebra",
    "difficulty": "medium",
    "time_taken": 1200,
    "date": "2024-01-01T00:00:00",
    "percentage": 80.0,
    "correct_answers": 8,
    "incorrect_answers": 2
  },
  "question_reviews": [
    {
      "question_index": 0,
      "question": "What is 2 + 2?",
      "options": ["3", "4", "5", "6"],
      "correct_answer": "4",
      "user_answer": "4",
      "is_correct": true,
      "explanation": "Basic addition"
    }
  ]
}
```

**Features:**
- Fetches from multiple result collections
- Enriches with assessment questions
- Normalizes answers for comparison
- Includes explanations for learning

---

### Notification APIs

#### 1. Get Notifications
**Backend Endpoint:** `GET /api/notifications/`  
**Frontend Service:** `notificationService.getNotifications()`  
**File Locations:**
- Backend: `backend/app/api/notifications.py` (Line 60-113)
- Frontend: `frontend/src/services/notificationService.ts` (Line 150-159)

**Response:**
```json
{
  "notifications": [
    {
      "id": "string",
      "_id": "string",
      "user_id": "string",
      "type": "general|batch_assignment|assessment_assigned",
      "title": "New Assessment",
      "message": "A new assessment has been assigned to you",
      "is_read": false,
      "created_at": "2024-01-01T00:00:00",
      "priority": "normal"
    }
  ],
  "unread_count": 5
}
```

**Features:**
- Queries by both `user_id` and `student_id` fields
- Sorted by creation date (newest first)
- Includes unread count
- Converts ObjectIds to strings for frontend

---

#### 2. Mark Notification as Read
**Backend Endpoint:** `POST /notifications/{notification_id}/read`  
**Frontend Service:** `notificationService.markNotificationAsRead()`  
**File Locations:**
- Backend: `backend/app/api/notifications.py` (Line 115-143)
- Frontend: `frontend/src/services/notificationService.ts` (Line 164-172)

**Response:**
```json
{
  "message": "Notification marked as read"
}
```

---

#### 3. Mark All Notifications as Read
**Backend Endpoint:** `POST /api/notifications/mark-all-read`  
**Frontend Service:** `notificationService.markAllNotificationsAsRead()`  
**File Locations:**
- Backend: `backend/app/api/notifications.py` (Line 145-168)
- Frontend: `frontend/src/services/notificationService.ts` (Line 177-185)

**Response:**
```json
{
  "message": "Marked 5 notifications as read"
}
```

---

#### 4. Delete Notification
**Backend Endpoint:** `DELETE /notifications/{notification_id}`  
**Frontend Service:** `notificationService.deleteNotification()`  
**File Locations:**
- Backend: `backend/app/api/notifications.py` (Line 170-197)
- Frontend: `frontend/src/services/notificationService.ts` (Line 190-198)

**Response:**
```json
{
  "message": "Notification deleted successfully"
}
```

---

#### 5. Get Unread Count
**Backend Endpoint:** `GET /api/notifications/unread-count`  
**File Locations:**
- Backend: `backend/app/api/notifications.py` (Line 199-219)

**Response:**
```json
{
  "unread_count": 5
}
```

---

### Bulk Operations APIs

#### 1. Upload Students in Bulk
**Backend Endpoint:** `POST /bulk-students/upload`  
**Frontend Service:** `bulkStudentService.uploadStudents()`  
**File Locations:**
- Backend: `backend/app/api/bulk_students.py`
- Frontend: `frontend/src/api/bulkStudentService.ts` (Line 79-105)

**Request:** Multipart form with Excel/CSV file
```
file: <excel_file>
batch_id: "string"
send_welcome_emails: "true"
```

**Response:**
```json
{
  "success": true,
  "total_rows": 50,
  "successful_imports": 48,
  "failed_imports": 2,
  "errors": [
    {
      "row": 5,
      "data": {"name": "John", "email": "john@example.com"},
      "errors": ["Email already exists"]
    }
  ],
  "created_students": [
    {
      "id": "string",
      "name": "Jane Doe",
      "roll_number": "2024001",
      "email": "jane@example.com",
      "row": 2
    }
  ],
  "batch_id": "string"
}
```

**Features:**
- Accepts Excel (.xlsx, .xls) or CSV files
- Validates email format and uniqueness
- Creates student accounts with generated passwords
- Adds students to specified batch
- Sends welcome emails (optional)
- Returns detailed error report

---

#### 2. Validate Student Upload File
**Backend Endpoint:** `POST /bulk-students/validate`  
**Frontend Service:** `bulkStudentService.validateFile()`  
**File Locations:**
- Frontend: `frontend/src/api/bulkStudentService.ts` (Line 110-130)

**Request:** Multipart form with Excel/CSV file

**Response:**
```json
{
  "success": true,
  "total_rows": 50,
  "valid_rows": 48,
  "invalid_rows": 2,
  "preview_data": [
    {
      "name": "John Doe",
      "roll_number": "2024001",
      "email": "john@example.com"
    }
  ],
  "errors": [
    {
      "row": 5,
      "data": {"name": "Invalid", "email": "invalid-email"},
      "errors": ["Invalid email format"]
    }
  ],
  "message": "Validation completed"
}
```

---

#### 3. Download Student Upload Template
**Backend Endpoint:** `GET /bulk-students/template`  
**Frontend Service:** `bulkStudentService.downloadTemplate()`  
**File Locations:**
- Frontend: `frontend/src/api/bulkStudentService.ts` (Line 135-165)

**Response:**
```json
{
  "template_data": [
    {
      "name": "John Doe",
      "roll_number": "2024001",
      "email": "john.doe@example.com"
    }
  ]
}
```

**Frontend Action:** Creates and downloads CSV file

---

#### 4. Get Upload History
**Backend Endpoint:** `GET /bulk-students/history/{batch_id}`  
**Frontend Service:** `bulkStudentService.getUploadHistory()`  
**File Locations:**
- Frontend: `frontend/src/api/bulkStudentService.ts` (Line 170-178)

**Response:**
```json
{
  "uploads": [
    {
      "_id": "string",
      "batch_id": "string",
      "uploaded_by": "string",
      "uploaded_at": "2024-01-01T00:00:00",
      "total_rows": 50,
      "successful_imports": 48,
      "failed_imports": 2,
      "file_name": "students.xlsx",
      "created_students": [],
      "errors": []
    }
  ]
}
```

---

#### 5. Upload Teachers in Bulk
**Backend Endpoint:** `POST /bulk-teachers/upload`  
**Frontend Service:** `bulkTeacherService.upload()`  
**File Locations:**
- Backend: `backend/app/api/bulk_teachers.py`
- Frontend: `frontend/src/api/bulkTeacherService.ts` (Line 22-27)

**Request:** Multipart form with Excel/CSV file

**Response:**
```json
{
  "success": true,
  "total_rows": 10,
  "successful_imports": 9,
  "failed_imports": 1,
  "errors": [
    {
      "row": 3,
      "email": "teacher@example.com",
      "error": "Email already exists"
    }
  ],
  "created_teachers": [
    {
      "id": "string",
      "name": "Jane Smith",
      "email": "jane@example.com",
      "teacher_id": "TCH1001",
      "row": 2
    }
  ]
}
```

---

#### 6. Validate Teacher Upload File
**Backend Endpoint:** `POST /bulk-teachers/validate`  
**Frontend Service:** `bulkTeacherService.validate()`  
**File Locations:**
- Frontend: `frontend/src/api/bulkTeacherService.ts` (Line 29-34)

**Request:** Multipart form with Excel/CSV file

**Response:**
```json
{
  "success": true,
  "total_rows": 10,
  "valid_rows": 9,
  "invalid_rows": 1,
  "preview_data": [],
  "errors": [],
  "message": "Validation completed"
}
```

---

#### 7. Download Teacher Upload Template
**Backend Endpoint:** `GET /bulk-teachers/template`  
**Frontend Service:** `bulkTeacherService.template()`  
**File Locations:**
- Frontend: `frontend/src/api/bulkTeacherService.ts` (Line 36-39)

**Response:**
```json
{
  "template_data": [
    {
      "name": "Alice Johnson",
      "email": "alice@example.com",
      "teacher_id": "TCH1001"
    }
  ]
}
```

---

#### 8. Get Teacher Upload History
**Backend Endpoint:** `GET /bulk-teachers/history`  
**Frontend Service:** `bulkTeacherService.history()`  
**File Locations:**
- Frontend: `frontend/src/api/bulkTeacherService.ts` (Line 41-44)

**Response:**
```json
{
  "uploads": []
}
```

---

### Health Check APIs

#### 1. Basic Health Check
**Backend Endpoint:** `GET /health/`  
**File Locations:**
- Backend: `backend/app/api/health.py` (Line 260-263)

**Response:**
```json
{
  "status": "healthy",
  "message": "API is running"
}
```

---

#### 2. Database Health Check
**Backend Endpoint:** `GET /health/db`  
**File Locations:**
- Backend: `backend/app/api/health.py` (Line 265-272)

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00",
  "database": {
    "connection": "ok",
    "response_time_ms": 15.23,
    "collections": 12,
    "data_size": 1048576,
    "storage_size": 2097152,
    "index_size": 524288
  }
}
```

---

#### 3. System Health Check
**Backend Endpoint:** `GET /health/system`  
**File Locations:**
- Backend: `backend/app/api/health.py` (Line 284-290)

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00",
  "system": {
    "cpu_percent": 23.5,
    "memory": {
      "total": 17179869184,
      "available": 8589934592,
      "used": 8589934592,
      "percent": 50.0
    },
    "disk": {
      "total": 1099511627776,
      "used": 549755813888,
      "free": 549755813888,
      "percent": 50.0
    },
    "process": {
      "memory_rss": 104857600,
      "memory_vms": 209715200,
      "cpu_percent": 5.2
    }
  }
}
```

---

#### 4. Application Health Check
**Backend Endpoint:** `GET /health/app`  
**File Locations:**
- Backend: `backend/app/api/health.py` (Line 292-299)

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00",
  "application": {
    "collections": {
      "users": {"status": "ok", "document_count": 500},
      "assessments": {"status": "ok", "document_count": 50},
      "batches": {"status": "ok", "document_count": 10},
      "notifications": {"status": "ok", "document_count": 150}
    },
    "recent_activity": {
      "assessments_created_24h": 5,
      "users_registered_24h": 10
    },
    "features": {
      "ai_generation": true,
      "notifications": true,
      "batch_management": true,
      "assessment_creation": true
    }
  }
}
```

---

#### 5. Comprehensive Health Check
**Backend Endpoint:** `GET /health/comprehensive`  
**File Locations:**
- Backend: `backend/app/api/health.py` (Line 301-334)

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00",
  "checks": {
    "basic": {"status": "healthy"},
    "database": {"status": "healthy"},
    "ai_service": {"status": "healthy"},
    "system": {"status": "healthy"},
    "application": {"status": "healthy"}
  }
}
```

---

#### 6. Health Metrics
**Backend Endpoint:** `GET /health/metrics`  
**File Locations:**
- Backend: `backend/app/api/health.py` (Line 336-364)

**Response:**
```json
{
  "timestamp": "2024-01-01T00:00:00",
  "metrics": {
    "cpu_percent": 23.5,
    "memory_percent": 50.0,
    "disk_percent": 50.0,
    "db_response_time_ms": 15.23,
    "db_collections": 12
  }
}
```

---

#### 7. Readiness Probe
**Backend Endpoint:** `GET /health/readiness`  
**File Locations:**
- Backend: `backend/app/api/health.py` (Line 366-391)

**Response:**
```json
{
  "status": "ready",
  "timestamp": "2024-01-01T00:00:00"
}
```

**Use Case:** Kubernetes readiness probe

---

#### 8. Liveness Probe
**Backend Endpoint:** `GET /health/liveness`  
**File Locations:**
- Backend: `backend/app/api/health.py` (Line 393-399)

**Response:**
```json
{
  "status": "alive",
  "timestamp": "2024-01-01T00:00:00"
}
```

**Use Case:** Kubernetes liveness probe

---

### AI Question APIs

#### 1. Create AI Question
**Backend Endpoint:** `POST /api/ai-questions/`  
**File Locations:**
- Backend: `backend/app/api/ai_questions.py` (Line 47-98)

**Request:**
```json
{
  "question": "What is 2 + 2?",
  "options": ["3", "4", "5", "6"],
  "answer": "4",
  "explanation": "Basic addition",
  "topic": "Mathematics",
  "difficulty": "easy",
  "generated_by": "gemini",
  "metadata": {}
}
```

**Response:**
```json
{
  "id": "string",
  "question": "What is 2 + 2?",
  "options": ["3", "4", "5", "6"],
  "answer": "4",
  "explanation": "Basic addition",
  "topic": "Mathematics",
  "difficulty": "easy",
  "generated_by": "gemini",
  "metadata": {},
  "created_at": "2024-01-01T00:00:00",
  "status": "active",
  "usage_count": 0,
  "quality_score": null
}
```

---

#### 2. Get AI Questions
**Backend Endpoint:** `GET /api/ai-questions/?topic={topic}&difficulty={difficulty}&status={status}&generated_by={generated_by}&limit={limit}&offset={offset}`  
**File Locations:**
- Backend: `backend/app/api/ai_questions.py` (Line 100-154)

**Query Parameters:**
- `topic`: Filter by topic (optional)
- `difficulty`: Filter by difficulty (optional)
- `status`: Filter by status (optional)
- `generated_by`: Filter by generator (optional)
- `limit`: Max results (1-100, default 50)
- `offset`: Pagination offset (default 0)

**Response:**
```json
[
  {
    "id": "string",
    "question": "What is 2 + 2?",
    "options": ["3", "4", "5", "6"],
    "answer": "4",
    "explanation": "Basic addition",
    "topic": "Mathematics",
    "difficulty": "easy",
    "generated_by": "gemini",
    "metadata": {},
    "created_at": "2024-01-01T00:00:00",
    "status": "active",
    "usage_count": 5,
    "quality_score": 4.5
  }
]
```

---

#### 3. Get AI Questions Statistics
**Backend Endpoint:** `GET /api/ai-questions/stats`  
**File Locations:**
- Backend: `backend/app/api/ai_questions.py` (Line 156-204)

**Response:**
```json
{
  "total_questions": 500,
  "active_questions": 450,
  "reviewed_questions": 30,
  "archived_questions": 20,
  "topic_stats": [
    {"_id": "Mathematics", "count": 150},
    {"_id": "Science", "count": 120}
  ],
  "difficulty_stats": [
    {"_id": "easy", "count": 200},
    {"_id": "medium", "count": 200},
    {"_id": "hard", "count": 100}
  ],
  "generator_stats": [
    {"_id": "gemini", "count": 450},
    {"_id": "openai", "count": 50}
  ]
}
```

---

#### 4. Update AI Question
**Backend Endpoint:** `PUT /api/ai-questions/{question_id}`  
**File Locations:**
- Backend: `backend/app/api/ai_questions.py` (Line 206-268)

**Request:**
```json
{
  "status": "reviewed",
  "quality_score": 4.5,
  "metadata": {}
}
```

**Response:**
```json
{
  "id": "string",
  "question": "What is 2 + 2?",
  "options": ["3", "4", "5", "6"],
  "answer": "4",
  "explanation": "Basic addition",
  "topic": "Mathematics",
  "difficulty": "easy",
  "generated_by": "gemini",
  "metadata": {},
  "created_at": "2024-01-01T00:00:00",
  "status": "reviewed",
  "usage_count": 5,
  "quality_score": 4.5
}
```

---

#### 5. Delete AI Question
**Backend Endpoint:** `DELETE /api/ai-questions/{question_id}`  
**File Locations:**
- Backend: `backend/app/api/ai_questions.py` (Line 270-304)

**Response:**
```json
{
  "success": true,
  "message": "AI question deleted successfully"
}
```

---

#### 6. Mark AI Question as Used
**Backend Endpoint:** `POST /api/ai-questions/{question_id}/use`  
**File Locations:**
- Backend: `backend/app/api/ai_questions.py` (Line 306-331)

**Response:**
```json
{
  "success": true,
  "message": "Question usage count updated"
}
```

**Use Case:** Track which AI-generated questions are being used in assessments

---

### Topic Configuration APIs

#### 1. Get Assessment Configuration
**Backend Endpoint:** `GET /api/topic/`  
**Frontend Service:** `assessmentService.getAssessmentConfig()`  
**File Locations:**
- Backend: `backend/app/api/topics.py` (Line 29-73)
- Frontend: `frontend/src/api/assessmentService.ts` (Line 135-138)

**Response:**
```json
{
  "success": true,
  "topic": "Python Programming",
  "qnCount": 10,
  "difficulty": "medium"
}
```

**Use Case:** Retrieve saved assessment preferences for a user

---

#### 2. Set Assessment Configuration
**Backend Endpoint:** `POST /api/topic/`  
**Frontend Service:** `assessmentService.setAssessmentConfig()`  
**File Locations:**
- Backend: `backend/app/api/topics.py` (Line 75-143)
- Frontend: `frontend/src/api/assessmentService.ts` (Line 127-130)

**Request:**
```json
{
  "topic": "Python Programming",
  "qnCount": 10,
  "difficulty": "medium"
}
```

**Response:**
```json
{
  "success": true,
  "topic": "Python Programming",
  "qnCount": 10,
  "difficulty": "medium"
}
```

**Features:**
- Validates topic, question count (1-50), and difficulty
- Stores configuration in `assessment_configs` collection
- Upserts (replaces existing config for user)

---

#### 3. Get Available Topics
**Backend Endpoint:** `GET /api/topic/available`  
**File Locations:**
- Backend: `backend/app/api/topics.py` (Line 145-166)

**Response:**
```json
{
  "success": true,
  "topics": [
    {
      "name": "Python Programming",
      "difficulty": ["easy", "medium", "hard"]
    },
    {
      "name": "JavaScript",
      "difficulty": ["easy", "medium", "hard"]
    },
    {
      "name": "Data Structures",
      "difficulty": ["medium", "hard"]
    },
    {
      "name": "Algorithms",
      "difficulty": ["medium", "hard"]
    },
    {
      "name": "Web Development",
      "difficulty": ["easy", "medium"]
    },
    {
      "name": "Database Design",
      "difficulty": ["medium", "hard"]
    }
  ]
}
```

---

## Frontend-Backend Mapping

### Frontend Service → Backend Endpoint Mapping

#### AuthService
| Frontend Method | Backend Endpoint | HTTP Method | Description |
|----------------|-----------------|-------------|-------------|
| `login()` | `/auth/login` | POST | User login with email/password |
| `register()` | `/auth/register` | POST | New user registration |
| `getCurrentUser()` | `/auth/status` | GET | Get current authenticated user |
| `logout()` | `/auth/logout` | POST | User logout |
| `isAuthenticated()` | N/A | Local | Check token in localStorage |
| `getToken()` | N/A | Local | Get token from localStorage |
| `setToken()` | N/A | Local | Store token in localStorage |
| `removeToken()` | N/A | Local | Remove token from localStorage |

---

#### AssessmentService
| Frontend Method | Backend Endpoint | HTTP Method | Description |
|----------------|-----------------|-------------|-------------|
| `setAssessmentConfig()` | `/api/topic` | POST | Save assessment preferences |
| `getAssessmentConfig()` | `/api/topic` | GET | Get assessment preferences |
| `createAssessment()` | `/api/assessments/` | POST | Create new assessment |
| `getTeacherAssessments()` | `/api/assessments/` | GET | Get teacher's assessments |
| `getAvailableAssessments()` | `/api/assessments/student/available` | GET | Get student's available assessments |
| `addQuestion()` | `/api/assessments/{id}/questions` | POST | Add question to assessment |
| `addCodingQuestion()` | `/api/assessments/{id}/coding-questions` | POST | Add coding question |
| `generateAIQuestions()` | `/api/assessments/{id}/ai-generate-questions` | POST | Generate AI questions |
| `publishAssessment()` | `/api/assessments/{id}/publish` | POST | Publish assessment |
| `assignToBatches()` | `/api/assessments/{id}/assign-batches` | POST | Assign to batches |
| `getAssessmentQuestions()` | `/api/assessments/{id}/questions` | GET | Get assessment questions |
| `submitAssessment()` | `/api/assessments/{id}/submit` | POST | Submit assessment |
| `submitCodingSolution()` | `/api/assessments/{id}/coding-submit` | POST | Submit coding solution |
| `getAssessmentDetails()` | `/api/assessments/{id}/details` | GET | Get assessment details |
| `getAssessmentLeaderboard()` | `/api/assessments/{id}/leaderboard` | GET | Get leaderboard |
| `getStudentNotifications()` | `/api/assessments/notifications` | GET | Get student notifications |
| `markNotificationRead()` | `/api/assessments/notifications/{id}/read` | POST | Mark notification as read |

---

#### CodingService
| Frontend Method | Backend Endpoint | HTTP Method | Description |
|----------------|-----------------|-------------|-------------|
| `generateProblem()` | `/api/coding/problems/generate` | POST | Generate coding problem |
| `getProblems()` | `/api/coding/problems` | GET | Get coding problems list |
| `getProblem()` | `/api/coding/problems/{id}` | GET | Get specific problem |
| `executeCode()` | `/api/coding/execute` | POST | Execute code with tests |
| `submitSolution()` | `/api/coding/submit` | POST | Submit solution |
| `getSubmission()` | `/api/coding/submissions/{id}` | GET | Get submission details |
| `startSession()` | `/api/coding/sessions/start` | POST | Start coding session |
| `updateSession()` | `/api/coding/sessions/{id}` | PUT | Update session data |
| `endSession()` | `/api/coding/sessions/{id}/end` | POST | End coding session |
| `getAnalytics()` | `/api/coding/analytics` | GET | Get coding analytics |
| `generateLearningPath()` | `/api/coding/analytics/learning-path` | POST | Generate learning path |

---

#### BulkStudentService
| Frontend Method | Backend Endpoint | HTTP Method | Description |
|----------------|-----------------|-------------|-------------|
| `uploadStudents()` | `/bulk-students/upload` | POST | Upload students file |
| `validateFile()` | `/bulk-students/validate` | POST | Validate upload file |
| `downloadTemplate()` | `/bulk-students/template` | GET | Download CSV template |
| `getUploadHistory()` | `/bulk-students/history/{batch_id}` | GET | Get upload history |
| `createTemplateFile()` | N/A | Local | Create template file locally |
| `validateFileFormat()` | N/A | Local | Validate file format locally |

---

#### BulkTeacherService
| Frontend Method | Backend Endpoint | HTTP Method | Description |
|----------------|-----------------|-------------|-------------|
| `upload()` | `/bulk-teachers/upload` | POST | Upload teachers file |
| `validate()` | `/bulk-teachers/validate` | POST | Validate upload file |
| `template()` | `/bulk-teachers/template` | GET | Download template |
| `history()` | `/bulk-teachers/history` | GET | Get upload history |
| `createTemplateCsv()` | N/A | Local | Create template file locally |

---

#### NotificationService
| Frontend Method | Backend Endpoint | HTTP Method | Description |
|----------------|-----------------|-------------|-------------|
| `getNotifications()` | `/api/notifications/` | GET | Get all notifications |
| `markNotificationAsRead()` | `/notifications/{id}/read` | POST | Mark notification as read |
| `markAllNotificationsAsRead()` | `/api/notifications/mark-all-read` | POST | Mark all as read |
| `deleteNotification()` | `/notifications/{id}` | DELETE | Delete notification |
| `useNotifications()` | N/A | Hook | React hook for notifications |
| `formatNotificationTime()` | N/A | Util | Format timestamp |
| `getNotificationIcon()` | N/A | Util | Get notification icon |

---

## Authentication Flow

### 1. Email/Password Login Flow
```
Frontend                      Backend                       Database
   |                             |                              |
   |--- POST /auth/login ------->|                              |
   |    (email, password)        |                              |
   |                             |--- Find user by email ------>|
   |                             |<--- User document -----------|
   |                             |                              |
   |                             |--- Verify password hash -----|
   |                             |                              |
   |                             |--- Generate JWT token -------|
   |                             |                              |
   |<--- JWT token + user -------|                              |
   |                             |                              |
   |--- Store token in localStorage                             |
   |                             |                              |
   |--- Redirect to dashboard ---|                              |
```

---

### 2. Google OAuth Flow
```
Frontend                      Backend                       Google
   |                             |                              |
   |--- GET /auth/google ------->|                              |
   |                             |--- Redirect to Google ------>|
   |<--------------------------- Redirect to Google consent ----|
   |                             |                              |
   |--- User approves ---------->|                              |
   |                             |<--- Authorization code ------|
   |                             |                              |
   |                             |--- Exchange code for token ->|
   |                             |<--- Access token -----------|
   |                             |                              |
   |                             |--- Get user info ----------->|
   |                             |<--- User profile -----------|
   |                             |                              |
   |                             |--- Create/Update user in DB--|
   |                             |--- Generate JWT token -------|
   |                             |                              |
   |<--- Redirect with JWT ------|                              |
   |                             |                              |
   |--- Store token in localStorage                             |
   |--- Redirect to dashboard ---|                              |
```

---

### 3. Face Recognition Login Flow
```
Frontend                      Backend                       Database
   |                             |                              |
   |--- Capture face image -----|                              |
   |--- Generate face descriptor|                              |
   |                             |                              |
   |--- POST /auth/face -------->|                              |
   |    (face_descriptor)        |                              |
   |                             |--- Find users with faces --->|
   |                             |<--- Users with face data ----|
   |                             |                              |
   |                             |--- Calculate Euclidean -------|
   |                             |    distance for each user    |
   |                             |--- Find best match ----------|
   |                             |                              |
   |                             |--- Generate JWT token -------|
   |                             |                              |
   |<--- JWT token + user -------|                              |
   |                             |                              |
   |--- Store token in localStorage                             |
   |--- Redirect to dashboard ---|                              |
```

---

## Error Handling

### Standard Error Response Format
```json
{
  "detail": "Error message here"
}
```

### Common HTTP Status Codes

| Status Code | Meaning | Common Scenarios |
|------------|---------|------------------|
| 200 | OK | Successful request |
| 201 | Created | Resource successfully created |
| 400 | Bad Request | Invalid input, validation error |
| 401 | Unauthorized | Missing or invalid JWT token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Duplicate resource (e.g., email exists) |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Server-side error |
| 503 | Service Unavailable | Service is down or unhealthy |

---

### Frontend Error Handling Pattern

```typescript
try {
  const result = await api.post('/endpoint', data);
  return result.data;
} catch (error: any) {
  console.error('Error:', error);
  
  if (error.response) {
    // Server responded with error
    const status = error.response.status;
    const detail = error.response.data?.detail || 'An error occurred';
    
    if (status === 401) {
      // Redirect to login
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    } else if (status === 403) {
      throw new Error('You do not have permission to perform this action');
    } else {
      throw new Error(detail);
    }
  } else if (error.request) {
    // Request made but no response
    throw new Error('Network error. Please check your connection.');
  } else {
    // Something else happened
    throw new Error('An unexpected error occurred');
  }
}
```

---

## Best Practices

### 1. Authentication
- **Always include JWT token** in Authorization header for protected endpoints
- **Refresh token** when it expires (requires re-login in current implementation)
- **Check token validity** before making API calls
- **Clear token** on logout and redirect to login

### 2. Error Handling
- **Catch all errors** in API calls
- **Display user-friendly messages** instead of raw error responses
- **Handle 401/403 errors** by redirecting to login or showing permission error
- **Log errors** for debugging but don't expose sensitive information to users

### 3. Performance
- **Cache static data** (e.g., available topics, batch lists)
- **Debounce search inputs** to reduce API calls
- **Use pagination** for large datasets
- **Implement loading states** to improve UX

### 4. Security
- **Never log tokens** or sensitive data
- **Validate input** on both frontend and backend
- **Sanitize user input** to prevent XSS attacks
- **Use HTTPS** in production
- **Implement rate limiting** on backend for sensitive endpoints

### 5. Code Organization
- **Centralize API calls** in service files
- **Use TypeScript interfaces** for request/response types
- **Keep API URLs** in a single configuration file
- **Reuse common patterns** (error handling, authentication)

---

## Migration Notes

### From Old Assessment System to New Teacher Assessments

**Collections:**
- Old: `assessments`
- New: `teacher_assessments`

**Key Differences:**
1. Teacher assessments use `teacher_id` instead of `created_by`
2. Batches are stored in `batches` field instead of `assigned_batches`
3. Results are stored in `teacher_assessment_results` instead of `assessment_submissions`

**Compatibility:**
- `/api/teacher/assessments` endpoint **only** reads from `teacher_assessments`
- `/api/assessments/` endpoint reads from **both** collections
- Student endpoints check **both** collections for available assessments

---

## Changelog

### Version 1.0.0 (Current)
- Initial comprehensive API documentation
- Complete frontend-backend mapping
- All authentication methods documented
- Assessment, coding, teacher, and admin endpoints
- Bulk operations support
- Health check endpoints
- AI question management

---

## Support & Contact

For questions or issues with the API:
1. Check this documentation first
2. Review the source code in the specified file locations
3. Check the backend logs for detailed error messages
4. Contact the development team

---

**Last Updated:** January 2025  
**API Version:** 1.0.0  
**Documentation Version:** 1.0.0

