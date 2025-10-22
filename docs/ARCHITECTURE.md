# modLRN System Architecture

## Overview

modLRN is a modern full-stack educational platform built with a microservices-inspired architecture, featuring a React frontend and FastAPI backend with MongoDB database.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                          FRONTEND LAYER                          │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   React 18   │  │  TypeScript  │  │   Vite 6.2   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Tailwind CSS │  │ Framer Motion│  │ Monaco Editor│          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              ▼
                         HTTP/HTTPS
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                          BACKEND LAYER                           │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    FastAPI 0.104.1                         │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐            │  │
│  │  │ Auth Router│ │Assessment  │ │ Coding     │  ...       │  │
│  │  │            │ │ Router     │ │ Router     │            │  │
│  │  └────────────┘ └────────────┘ └────────────┘            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   Business Logic Layer                     │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐            │  │
│  │  │ Assessment │ │   Gemini   │ │   Judge0   │            │  │
│  │  │  Service   │ │  Service   │ │  Service   │            │  │
│  │  └────────────┘ └────────────┘ └────────────┘            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Data Access Layer                       │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐            │  │
│  │  │  Motor     │ │  Pydantic  │ │  Sessions  │            │  │
│  │  │ (Async DB) │ │ Validation │ │  Manager   │            │  │
│  │  └────────────┘ └────────────┘ └────────────┘            │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        DATABASE LAYER                            │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                      MongoDB                              │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐            │  │
│  │  │   users    │ │ assessments│ │  batches   │            │  │
│  │  └────────────┘ └────────────┘ └────────────┘            │  │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐            │  │
│  │  │ ai_questions│ │notifications│ │  results  │            │  │
│  │  └────────────┘ └────────────┘ └────────────┘            │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      EXTERNAL SERVICES                           │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Google Gemini│  │   Judge0 API │  │ Google OAuth │          │
│  │      AI      │  │              │  │              │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

## Layer Breakdown

### 1. Frontend Layer

#### Technology Stack
- **React 18**: Modern React with hooks and concurrent features
- **TypeScript**: Type-safe JavaScript for better code quality
- **Vite 6.2**: Fast build tool and development server
- **Tailwind CSS**: Utility-first CSS framework
- **Framer Motion**: Animation library for smooth transitions
- **Monaco Editor**: VS Code's code editor for coding challenges

#### Architecture Pattern
- **Component-Based**: Modular, reusable UI components
- **Container/Presentational Pattern**: Separation of business logic and UI
- **Context API**: Global state management for auth, theme, toast
- **Custom Hooks**: Reusable stateful logic (useAuth, useAssessments, etc.)

#### Directory Structure
```
frontend/src/
├── api/            # API service layer
├── components/     # Reusable components
│   ├── ui/        # Base UI components
│   ├── teacher/   # Teacher-specific components
│   └── admin/     # Admin-specific components
├── contexts/       # React Context providers
├── hooks/          # Custom React hooks
├── pages/          # Page components (routes)
├── services/       # Business logic services
├── types/          # TypeScript type definitions
└── utils/          # Utility functions
```

### 2. Backend Layer

#### Technology Stack
- **FastAPI 0.104.1**: Modern, fast web framework
- **Python 3.8+**: Programming language
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation
- **Motor**: Async MongoDB driver
- **Python-Jose**: JWT authentication
- **Passlib**: Password hashing

#### Architecture Pattern
- **Clean Architecture**: Separation of concerns
- **Repository Pattern**: Data access abstraction
- **Service Layer**: Business logic encapsulation
- **Dependency Injection**: FastAPI's dependency system

#### Directory Structure
```
backend/app/
├── api/               # API endpoints (routers)
│   ├── admin/        # Admin endpoints
│   ├── assessments/  # Assessment endpoints
│   ├── coding_modules/  # Coding platform endpoints
│   └── teacher_modules/  # Teacher endpoints
├── core/              # Core configuration
├── db/                # Database configuration
├── models/            # Data models
├── schemas/           # Pydantic schemas
├── services/          # Business logic
├── middleware/        # Custom middleware
├── utils/             # Utility functions
└── dependencies.py    # Dependency injection
```

### 3. Database Layer

#### MongoDB Collections

**users**
- User accounts (students, teachers, admins)
- Authentication data
- Profile information
- Progress tracking

**batches**
- Student groups
- Batch information
- Teacher assignments

**assessments**
- Manual assessments
- Configuration
- Questions

**teacher_assessments**
- AI-generated assessments
- Created by teachers
- Batch assignments

**ai_questions**
- AI-generated questions
- Question bank
- Review status

**teacher_assessment_results**
- Student submissions
- Scores and feedback
- Performance data

**notifications**
- User notifications
- System alerts
- Assignment notifications

**coding_problems**
- Coding challenges
- Test cases
- Solutions

### 4. External Services

#### Google Gemini AI
- **Purpose**: AI question generation
- **Integration**: GeminiCodingService
- **Features**:
  - Topic-based question generation
  - Difficulty-adaptive questions
  - Explanation generation

#### Judge0 API
- **Purpose**: Code execution
- **Integration**: Judge0ExecutionService
- **Features**:
  - Multi-language support (10+ languages)
  - Sandboxed execution
  - Resource limits

#### Google OAuth 2.0
- **Purpose**: Social authentication
- **Integration**: Google OAuth flow
- **Features**:
  - Single sign-on
  - Secure authentication
  - Profile data access

## Data Flow

### 1. Authentication Flow

```
┌─────────┐   1. Login Request    ┌─────────┐
│ Browser │ ───────────────────> │ Backend │
└─────────┘                       └─────────┘
     ▲                                  │
     │                                  │ 2. Validate
     │                                  ▼
     │                             ┌─────────┐
     │    4. JWT Token            │ MongoDB │
     │    <───────────────────    └─────────┘
     │                                  │
     │                                  │ 3. User Found
     │                                  ▼
     │                             ┌─────────┐
     └──────────────────────────  │ Generate│
        5. Store in localStorage   │   JWT   │
                                   └─────────┘
```

### 2. Assessment Creation Flow

```
┌────────┐  1. Create Request   ┌────────┐
│Teacher │ ──────────────────> │Backend │
└────────┘                      └────────┘
                                    │
                                    │ 2. Validate
                                    ▼
                               ┌──────────┐
                               │  Gemini  │
                               │    AI    │
                               └──────────┘
                                    │
                                    │ 3. Generate Questions
                                    ▼
                               ┌──────────┐
                               │ MongoDB  │
                               └──────────┘
                                    │
                                    │ 4. Store Assessment
                                    ▼
                               ┌──────────┐
                               │  Notify  │
                               │ Students │
                               └──────────┘
```

### 3. Code Execution Flow

```
┌─────────┐  1. Submit Code    ┌─────────┐
│ Student │ ─────────────────> │ Backend │
└─────────┘                     └─────────┘
                                     │
                                     │ 2. Validate & Sanitize
                                     ▼
                                ┌──────────┐
                                │ Judge0   │
                                │   API    │
                                └──────────┘
                                     │
                                     │ 3. Execute in Sandbox
                                     ▼
                                ┌──────────┐
                                │  Result  │
                                │  Output  │
                                └──────────┘
                                     │
                                     │ 4. Store & Return
                                     ▼
                                ┌──────────┐
                                │ MongoDB  │
                                └──────────┘
```

## Security Architecture

### 1. Authentication & Authorization

```
Request → Middleware → JWT Validation → Role Check → Handler
            ▲              │                │
            │              ▼                ▼
       Rate Limit      Decode Token    Check Permissions
```

**Layers**:
1. **Rate Limiting**: SlowAPI for request throttling
2. **JWT Validation**: Verify token signature and expiration
3. **Role-Based Access Control**: Check user permissions
4. **Resource Authorization**: Verify ownership/access rights

### 2. Data Protection

- **Password Hashing**: Bcrypt with salt
- **JWT Tokens**: HS256 algorithm
- **HTTPS Only**: SSL/TLS encryption
- **Input Validation**: Pydantic schemas
- **SQL Injection Prevention**: MongoDB parameterized queries
- **XSS Protection**: Input sanitization

### 3. Code Execution Security

- **Sandboxed Environment**: Judge0 containers
- **Resource Limits**: CPU, memory, time constraints
- **Network Isolation**: No external access
- **Code Review**: Pre-execution validation

## Scalability Considerations

### 1. Horizontal Scaling

- **Stateless Backend**: JWT-based authentication
- **Load Balancer**: Distribute requests across instances
- **Database Sharding**: Distribute data across servers
- **CDN**: Static asset delivery

### 2. Vertical Scaling

- **Database Indexing**: Fast query performance
- **Connection Pooling**: Efficient database connections
- **Caching Layer**: Redis for session/data caching
- **Background Tasks**: Celery for async processing

### 3. Performance Optimization

- **Lazy Loading**: Load data on demand
- **Pagination**: Limit result sets
- **Compression**: Gzip responses
- **Async Operations**: Non-blocking I/O

## Deployment Architecture

### Production Environment

```
┌─────────────────────────────────────────────────────────┐
│                      Load Balancer                       │
│                    (Nginx/CloudFlare)                    │
└─────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
  ┌──────────┐     ┌──────────┐     ┌──────────┐
  │ Frontend │     │ Backend  │     │ Backend  │
  │ (Vercel) │     │Instance 1│     │Instance 2│
  └──────────┘     └──────────┘     └──────────┘
                          │
                          ▼
                  ┌───────────────┐
                  │   MongoDB     │
                  │   (Atlas)     │
                  └───────────────┘
                          │
              ┌───────────┼───────────┐
              ▼           ▼           ▼
        ┌─────────┐ ┌─────────┐ ┌─────────┐
        │Replica 1│ │Replica 2│ │Replica 3│
        └─────────┘ └─────────┘ └─────────┘
```

## Monitoring & Logging

### 1. Application Logging

- **Structured Logging**: JSON format
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Log Rotation**: Daily rotation with retention
- **Centralized Logging**: CloudWatch/ELK Stack

### 2. Monitoring

- **Health Checks**: `/api/health` endpoint
- **Metrics Collection**: Request counts, response times
- **Error Tracking**: Sentry integration
- **Performance Monitoring**: New Relic/DataDog

### 3. Analytics

- **User Analytics**: Vercel Analytics
- **API Analytics**: Request patterns, usage statistics
- **Database Analytics**: Query performance, indexing

## API Design Principles

### RESTful Architecture

- **Resource-Based URLs**: `/api/assessments`, `/api/users`
- **HTTP Methods**: GET, POST, PUT, DELETE
- **Status Codes**: Appropriate HTTP status codes
- **JSON Format**: Request/response in JSON

### API Versioning

- **URL Versioning**: `/api/v1/resource`
- **Backward Compatibility**: Maintain old versions
- **Deprecation Policy**: 6-month notice

### Response Format

```json
{
  "success": true,
  "data": {...},
  "message": "Operation successful",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Technology Choices & Rationale

### Frontend

**React**: Component reusability, large ecosystem, performance
**TypeScript**: Type safety, better IDE support, fewer runtime errors
**Vite**: Fast builds, modern tooling, HMR
**Tailwind CSS**: Utility-first, consistent design, small bundle

### Backend

**FastAPI**: High performance, automatic docs, type hints
**MongoDB**: Flexible schema, horizontal scaling, JSON-like documents
**Motor**: Async driver for MongoDB, better performance
**Pydantic**: Data validation, serialization, automatic docs

### External Services

**Gemini AI**: Advanced AI capabilities, cost-effective, reliable
**Judge0**: Multi-language support, sandboxed execution, proven reliability
**Google OAuth**: Trusted provider, easy integration, secure

## Future Architecture Enhancements

### 1. Microservices Migration

- Split monolith into separate services
- API Gateway for routing
- Service mesh for communication
- Independent deployment

### 2. Real-Time Features

- WebSocket integration
- Live notifications
- Real-time collaboration
- Live leaderboards

### 3. Advanced AI Features

- Personalized learning paths
- Adaptive difficulty
- Plagiarism detection
- Code review AI

### 4. Mobile Applications

- React Native apps
- Native iOS/Android apps
- Offline mode support
- Push notifications

---

This architecture is designed for scalability, maintainability, and extensibility while maintaining high performance and security standards.

