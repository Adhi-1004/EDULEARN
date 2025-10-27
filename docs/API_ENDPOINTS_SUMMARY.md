# API Endpoints Quick Reference

This is a quick reference guide for all API endpoints in EDULEARN. For complete documentation with request/response examples and detailed explanations, see **[COMPLETE_API_REFERENCE.md](./COMPLETE_API_REFERENCE.md)**.

---

## Authentication Endpoints (`/auth`)

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/auth/register` | POST | Register new user | No |
| `/auth/login` | POST | Login with email/password | No |
| `/auth/face` | POST | Login with face recognition | No |
| `/auth/face-status` | GET | Check if user has registered face | Yes |
| `/auth/register-face` | POST | Register face descriptor | Yes |
| `/auth/google` | GET | Initiate Google OAuth login | No |
| `/auth/google/callback` | GET | Google OAuth callback | No |
| `/auth/logout` | POST | Logout user | Yes |
| `/auth/status` | GET | Get current authentication status | Yes |

---

## User Management Endpoints (`/api/users`)

| Endpoint | Method | Description | Auth Required | Role |
|----------|--------|-------------|---------------|------|
| `/api/users/` | GET | Get all users (paginated) | Yes | Admin |
| `/api/users/me` | GET | Get current user profile | Yes | Any |
| `/api/users/me` | PUT | Update current user profile | Yes | Any |
| `/api/users/{user_id}` | GET | Get specific user | Yes | Teacher/Admin |
| `/api/users/{user_id}` | PUT | Update user | Yes | Admin |
| `/api/users/{user_id}` | DELETE | Delete user | Yes | Admin |
| `/api/users/{user_id}/gamification` | GET | Get user gamification data | Yes | Any |
| `/api/users/{user_id}/badges` | GET | Get user badges | Yes | Any |
| `/api/users/{user_id}/update-activity` | POST | Update user activity | Yes | Any |
| `/api/users/stats/overview` | GET | Get user statistics | Yes | Admin |

---

## Assessment Endpoints (`/api/assessments`)

| Endpoint | Method | Description | Auth Required | Role |
|----------|--------|-------------|---------------|------|
| `/api/assessments/` | POST | Create assessment | Yes | Teacher |
| `/api/assessments/` | GET | Get teacher's assessments | Yes | Teacher |
| `/api/assessments/{id}/details` | GET | Get assessment details | Yes | Any |
| `/api/assessments/{id}/publish` | POST | Publish assessment | Yes | Teacher |
| `/api/assessments/{id}/assign-batches` | POST | Assign to batches | Yes | Teacher |
| `/api/assessments/student/available` | GET | Get available assessments | Yes | Student |
| `/api/assessments/student/upcoming` | GET | Get upcoming assessments | Yes | Student |
| `/api/assessments/{id}/submit` | POST | Submit assessment | Yes | Student |
| `/api/assessments/{id}/coding-submit` | POST | Submit coding solution | Yes | Student |
| `/api/assessments/{id}/leaderboard` | GET | Get assessment leaderboard | Yes | Any |

---

## Coding Platform Endpoints (`/api/coding`)

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/coding/problems/generate` | POST | Generate coding problem (AI) | Yes |
| `/api/coding/problems` | GET | Get coding problems list | Yes |
| `/api/coding/problems/{id}` | GET | Get specific problem | Yes |
| `/api/coding/execute` | POST | Execute code with test cases | Yes |
| `/api/coding/submit` | POST | Submit coding solution | Yes |
| `/api/coding/submissions/{id}` | GET | Get submission details | Yes |
| `/api/coding/sessions/start` | POST | Start coding session | Yes |
| `/api/coding/sessions/{id}` | PUT | Update session data | Yes |
| `/api/coding/sessions/{id}/end` | POST | End coding session | Yes |
| `/api/coding/analytics` | GET | Get coding analytics | Yes |
| `/api/coding/analytics/learning-path` | POST | Generate learning path (AI) | Yes |

---

## Teacher Endpoints (`/api/teacher`)

| Endpoint | Method | Description | Auth Required | Role |
|----------|--------|-------------|---------------|------|
| `/api/teacher/dashboard` | GET | Get teacher dashboard | Yes | Teacher |
| `/api/teacher/batches` | GET | Get teacher's batches | Yes | Teacher |
| `/api/teacher/batches` | POST | Create new batch | Yes | Teacher |
| `/api/teacher/batches/{id}` | DELETE | Delete batch | Yes | Teacher |
| `/api/teacher/students` | GET | Get students (filtered) | Yes | Teacher |
| `/api/teacher/students/add` | POST | Add student to batch | Yes | Teacher |
| `/api/teacher/students/remove` | POST | Remove student from batch | Yes | Teacher |
| `/api/teacher/assessments` | GET | Get teacher's assessments | Yes | Teacher |
| `/api/teacher/assessments/create` | POST | Create teacher assessment | Yes | Teacher |
| `/api/teacher/generate-student-report` | POST | Generate AI report | Yes | Teacher |
| `/api/teacher/ai-reports/{teacher_id}` | GET | Get AI reports | Yes | Teacher |
| `/api/teacher/health` | GET | Health check | No | Any |

---

## Admin Endpoints (`/api/admin`)

| Endpoint | Method | Description | Auth Required | Role |
|----------|--------|-------------|---------------|------|
| `/api/admin/analytics/platform` | GET | Get platform statistics | Yes | Admin |
| `/api/admin/users/activity` | GET | Get user activity | Yes | Admin |
| `/api/admin/system/health` | GET | Get system health | Yes | Admin |
| `/api/admin/users/bulk-import` | POST | Bulk import users | Yes | Admin |
| `/api/admin/users/export` | GET | Export users | Yes | Admin |
| `/api/admin/users/{id}/reset-password` | POST | Reset user password | Yes | Admin |
| `/api/admin/users` | GET | Get all users | Yes | Admin |
| `/api/admin/users` | POST | Create user | Yes | Admin |
| `/api/admin/users/{id}` | PUT | Update user | Yes | Admin |
| `/api/admin/users/{id}` | DELETE | Delete user | Yes | Admin |
| `/api/admin/users/{id}/details` | GET | Get user details | Yes | Admin |
| `/api/admin/analytics/content` | GET | Get content analytics | Yes | Admin |
| `/api/admin/analytics/teachers` | GET | Get teacher performance | Yes | Admin |
| `/api/admin/analytics/performance` | GET | Get system performance | Yes | Admin |

---

## Notification Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/notifications/` | GET | Get all notifications | Yes |
| `/notifications/{id}/read` | POST | Mark notification as read | Yes |
| `/api/notifications/mark-all-read` | POST | Mark all as read | Yes |
| `/notifications/{id}` | DELETE | Delete notification | Yes |
| `/api/notifications/unread-count` | GET | Get unread count | Yes |

---

## Results Endpoints (`/api/results`)

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/results/user/{user_id}` | GET | Get user results | Yes |
| `/api/results/analytics/{user_id}` | GET | Get user analytics | Yes |
| `/api/results/` | POST | Submit assessment result | Yes |
| `/api/results/{id}/detailed` | GET | Get detailed result | Yes |
| `/api/results/health` | GET | Health check | No |

---

## Bulk Operations Endpoints

| Endpoint | Method | Description | Auth Required | Role |
|----------|--------|-------------|---------------|------|
| `/bulk-students/upload` | POST | Upload students (Excel/CSV) | Yes | Teacher |
| `/bulk-students/validate` | POST | Validate upload file | Yes | Teacher |
| `/bulk-students/template` | GET | Download template | No | Any |
| `/bulk-students/history/{batch_id}` | GET | Get upload history | Yes | Teacher |
| `/bulk-teachers/upload` | POST | Upload teachers (Excel/CSV) | Yes | Admin |
| `/bulk-teachers/validate` | POST | Validate upload file | Yes | Admin |
| `/bulk-teachers/template` | GET | Download template | No | Any |
| `/bulk-teachers/history` | GET | Get upload history | Yes | Admin |

---

## Topic Configuration Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/topic/` | GET | Get assessment config | Yes |
| `/api/topic/` | POST | Set assessment config | Yes |
| `/api/topic/available` | GET | Get available topics | No |

---

## AI Questions Endpoints (`/api/ai-questions`)

| Endpoint | Method | Description | Auth Required | Role |
|----------|--------|-------------|---------------|------|
| `/api/ai-questions/` | POST | Create AI question | Yes | Any |
| `/api/ai-questions/` | GET | Get AI questions | Yes | Admin |
| `/api/ai-questions/stats` | GET | Get AI questions stats | Yes | Admin |
| `/api/ai-questions/{id}` | PUT | Update AI question | Yes | Admin |
| `/api/ai-questions/{id}` | DELETE | Delete AI question | Yes | Admin |
| `/api/ai-questions/{id}/use` | POST | Mark question as used | Yes | Any |

---

## Health Check Endpoints (`/health`)

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/health/` | GET | Basic health check | No |
| `/health/db` | GET | Database health | No |
| `/health/ai` | GET | AI service health | No |
| `/health/system` | GET | System resources health | No |
| `/health/app` | GET | Application health | No |
| `/health/comprehensive` | GET | All health checks | No |
| `/health/metrics` | GET | Health metrics | No |
| `/health/readiness` | GET | Kubernetes readiness probe | No |
| `/health/liveness` | GET | Kubernetes liveness probe | No |

---

## Endpoint Statistics

- **Total Endpoints:** 100+
- **Authentication Methods:** JWT, Google OAuth, Face Recognition
- **Role-Based Access:** Student, Teacher, Admin
- **AI-Powered Features:** 10+ endpoints
- **Bulk Operations:** 8 endpoints
- **Health Monitoring:** 9 endpoints

---

## Frontend Services Mapping

### AuthService
- Handles all authentication endpoints
- Manages token storage and validation
- Provides authentication state management

### AssessmentService
- Complete assessment lifecycle management
- Question generation and submission
- Leaderboard and notifications

### CodingService
- Coding problem generation and management
- Code execution and submission
- Analytics and learning paths

### BulkStudentService
- Bulk student upload and validation
- Template download
- Upload history tracking

### BulkTeacherService
- Bulk teacher upload and validation
- Template management
- History tracking

### NotificationService
- Real-time notifications
- Read/unread management
- Notification cleanup

---

## Quick Links

- **[Complete API Reference](./COMPLETE_API_REFERENCE.md)** - Full API documentation with examples
- **[Architecture Overview](./ARCHITECTURE.md)** - System architecture
- **[Database Schema](./DATABASE_SCHEMA.md)** - MongoDB collections
- **[Features Guide](./FEATURES.md)** - Feature documentation

---

**Last Updated:** January 2025


