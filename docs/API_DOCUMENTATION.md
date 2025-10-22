# EDULEARN API Documentation

## Overview

EDULEARN is a comprehensive educational assessment platform that provides APIs for creating, managing, and analyzing assessments.

### Base URL
```
https://api.edulearn.com
```

### Authentication
All protected endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## API Endpoints


## User Registration

**Method:** `POST`  
**Path:** `/api/auth/register`  
**Description:** Register a new user account

### Parameters

No parameters required.

### Request Body


**Schema:** `UserCreate`

```json
{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "password": "securePassword123",
  "role": "student"
}
```


### Response


**Status:** `201 Created`  
**Schema:** `UserResponse`

```json
{
  "id": "user_123",
  "name": "John Doe",
  "email": "john.doe@example.com",
  "role": "student",
  "created_at": "2024-01-01T00:00:00Z"
}
```


### Example Request

```bash
curl -X POST "https://api.edulearn.com/api/auth/register" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Example Response

```json
{}
```

### Error Responses

- **400**: Invalid input data
- **409**: Email already exists

---


## User Login

**Method:** `POST`  
**Path:** `/api/auth/login`  
**Description:** Authenticate user and get JWT token

### Parameters

No parameters required.

### Request Body


**Schema:** `UserLogin`

```json
{
  "email": "john.doe@example.com",
  "password": "securePassword123"
}
```


### Response


**Status:** `200 OK`  
**Schema:** `LoginResponse`

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": "user_123",
    "name": "John Doe",
    "email": "john.doe@example.com",
    "role": "student"
  }
}
```


### Example Request

```bash
curl -X POST "https://api.edulearn.com/api/auth/login" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Example Response

```json
{}
```

### Error Responses

- **401**: Invalid credentials
- **422**: Validation error

---


## Create Assessment

**Method:** `POST`  
**Path:** `/api/assessments`  
**Description:** Create a new assessment

### Parameters

- **Authorization** (header): JWT token

### Request Body


**Schema:** `AssessmentCreate`

```json
{
  "title": "Mathematics Assessment - Algebra Basics",
  "description": "Comprehensive assessment covering basic algebraic concepts",
  "subject": "Mathematics",
  "difficulty": "intermediate",
  "time_limit": 60,
  "questions": [
    {
      "question": "What is the value of x in the equation 2x + 5 = 13?",
      "options": [
        "3",
        "4",
        "5",
        "6"
      ],
      "correct_answer": 0,
      "explanation": "Solving: 2x + 5 = 13, 2x = 8, x = 4"
    }
  ],
  "max_attempts": 3,
  "type": "mcq",
  "batches": [
    "batch_1",
    "batch_2"
  ]
}
```


### Response


**Status:** `201 Created`  
**Schema:** `AssessmentResponse`

```json
{
  "id": "assessment_123",
  "title": "Mathematics Assessment - Algebra Basics",
  "description": "Comprehensive assessment covering basic algebraic concepts",
  "subject": "Mathematics",
  "difficulty": "intermediate",
  "time_limit": 60,
  "total_questions": 1,
  "created_by": "teacher_456",
  "created_at": "2024-01-01T00:00:00Z",
  "is_active": true
}
```


### Example Request

```bash
curl -X POST "https://api.edulearn.com/api/assessments" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Example Response

```json
{}
```

### Error Responses

- **401**: Unauthorized
- **403**: Insufficient permissions
- **422**: Validation error

---


## Get Assessment Questions

**Method:** `GET`  
**Path:** `/api/assessments/{assessment_id}/questions`  
**Description:** Get questions for a specific assessment

### Parameters

- **assessment_id** (path): Assessment ID
- **Authorization** (header): JWT token

### Request Body

No request body required.

### Response


**Status:** `200 OK`  
**Schema:** `AssessmentQuestionsResponse`

```json
{
  "assessment_id": "assessment_123",
  "title": "Mathematics Assessment - Algebra Basics",
  "questions": [
    {
      "id": "question_1",
      "question": "What is the value of x in the equation 2x + 5 = 13?",
      "options": [
        "3",
        "4",
        "5",
        "6"
      ],
      "type": "mcq"
    }
  ],
  "time_limit": 60,
  "total_questions": 1
}
```


### Example Request

```bash
curl -X GET "https://api.edulearn.com/api/assessments/{assessment_id}/questions" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Example Response

```json
{}
```

### Error Responses

- **401**: Unauthorized
- **404**: Assessment not found
- **403**: Access denied

---


## Submit Assessment

**Method:** `POST`  
**Path:** `/api/assessments/{assessment_id}/submit`  
**Description:** Submit assessment answers

### Parameters

- **assessment_id** (path): Assessment ID
- **Authorization** (header): JWT token

### Request Body


**Schema:** `AssessmentSubmission`

```json
{
  "answers": [
    {
      "question_id": "question_1",
      "answer": 1,
      "time_taken": 30
    }
  ],
  "total_time": 30
}
```


### Response


**Status:** `200 OK`  
**Schema:** `AssessmentResult`

```json
{
  "assessment_id": "assessment_123",
  "student_id": "student_456",
  "score": 0,
  "total_questions": 1,
  "correct_answers": 0,
  "incorrect_answers": 1,
  "time_taken": 30,
  "submitted_at": "2024-01-01T00:00:00Z",
  "answers": [
    {
      "question_id": "question_1",
      "answer": 1,
      "correct_answer": 0,
      "is_correct": false,
      "time_taken": 30
    }
  ]
}
```


### Example Request

```bash
curl -X POST "https://api.edulearn.com/api/assessments/{assessment_id}/submit" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Example Response

```json
{}
```

### Error Responses

- **401**: Unauthorized
- **404**: Assessment not found
- **422**: Validation error

---


## Error Handling

All API errors return structured JSON responses:

```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_CREDENTIALS` | 401 | Invalid email/password |
| `TOKEN_EXPIRED` | 401 | JWT token has expired |
| `INSUFFICIENT_PERMISSIONS` | 403 | User lacks required permissions |
| `RESOURCE_NOT_FOUND` | 404 | Requested resource doesn't exist |
| `VALIDATION_ERROR` | 422 | Request data validation failed |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |

## Rate Limiting

API requests are rate-limited to ensure fair usage:

| Category | Limit | Window |
|----------|-------|--------|
| General API | 100 requests | 1 minute |
| Assessment Creation | 10 requests | 1 minute |
| Code Execution | 20 requests | 1 minute |

## SDKs and Libraries

### JavaScript/TypeScript
```bash
npm install @edulearn/api-client
```

### Python
```bash
pip install edulearn-api
```

## Support

For API support and questions:
- Email: support@edulearn.com
- Documentation: https://docs.edulearn.com
- Status Page: https://status.edulearn.com