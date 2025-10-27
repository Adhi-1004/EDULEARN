# 🔐 Authentication & User Management Features

## Table of Contents
1. [Overview](#overview)
2. [Email/Password Authentication](#emailpassword-authentication)
3. [Face Recognition Authentication](#face-recognition-authentication)
4. [Google OAuth Authentication](#google-oauth-authentication)
5. [Session Management](#session-management)
6. [User Profile Management](#user-profile-management)
7. [Role-Based Access Control](#role-based-access-control)
8. [Password Reset](#password-reset)

---

## Overview

The EDULEARN platform implements a comprehensive authentication system supporting multiple login methods while maintaining security through JWT tokens and role-based access control.

### Authentication Methods Supported
- ✉️ Email/Password Authentication
- 👤 Face Recognition Authentication
- 🔗 Google OAuth 2.0
- 🎫 JWT Token-based Sessions

### Security Features
- Password hashing with bcrypt
- JWT access and refresh tokens
- HTTP-only cookies for token storage
- Role-based authorization (Student, Teacher, Admin)
- Session validation and expiry

---

## Email/Password Authentication

### Feature Overview
Traditional authentication using email and password credentials with secure password hashing.

### 1. User Registration Flow

#### Process Diagram
```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   User UI    │         │   Frontend   │         │   Backend    │
│  (Register   │         │   Service    │         │   API        │
│   Page)      │         │              │         │              │
└──────┬───────┘         └──────┬───────┘         └──────┬───────┘
       │                        │                        │
       │ 1. Fill Form          │                        │
       │    (name, email,      │                        │
       │     password, role)   │                        │
       │                        │                        │
       │ 2. Submit Form        │                        │
       ├───────────────────────▶│                        │
       │                        │                        │
       │                        │ 3. POST /auth/register│
       │                        │    {name, email,      │
       │                        │     password, role}   │
       │                        ├───────────────────────▶│
       │                        │                        │
       │                        │                        │ 4. Validate Data
       │                        │                        │    (Pydantic)
       │                        │                        │
       │                        │                        │ 5. Check if User Exists
       │                        │                        │    (MongoDB Query)
       │                        │                        ├────────┐
       │                        │                        │        │
       │                        │                        │◀───────┘
       │                        │                        │
       │                        │                        │ 6. Hash Password
       │                        │                        │    (bcrypt)
       │                        │                        │
       │                        │                        │ 7. Create User Doc
       │                        │                        │    {id, name, email,
       │                        │                        │     hashed_pwd, role,
       │                        │                        │     created_at}
       │                        │                        │
       │                        │                        │ 8. Insert into DB
       │                        │                        ├─────────┐
       │                        │                        │         │
       │                        │                        │◀────────┘
       │                        │                        │
       │                        │                        │ 9. Initialize
       │                        │                        │    Gamification
       │                        │                        │    (XP=0, Level=1)
       │                        │                        │
       │                        │  10. Response         │
       │                        │      {message,        │
       │                        │       user_data}      │
       │                        │◀───────────────────────┤
       │                        │                        │
       │ 11. Redirect to Login │                        │
       │◀───────────────────────┤                        │
       │                        │                        │
       ▼                        ▼                        ▼
```

#### Files Involved

**Frontend:**
- `frontend/src/pages/Register.tsx` - Registration page UI
- `frontend/src/api/authService.ts` - Authentication service
  - Function: `register(userData: RegisterData)`

**Backend:**
- `backend/app/api/auth.py` - Authentication endpoints
  - Endpoint: `POST /api/auth/register`
  - Function: `register(user_data: UserRegister)`
- `backend/app/models/user.py` - User data models
- `backend/app/utils/security.py` - Password hashing utilities

**Database:**
- Collection: `users`
- Collection: `user_stats` (for gamification)

#### Request Flow

**1. Frontend Request**
```typescript
// File: frontend/src/api/authService.ts
export const register = async (userData: RegisterData) => {
  const response = await api.post('/auth/register', userData);
  return response.data;
};
```

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePassword123!",
  "role": "student"
}
```

**2. Backend Processing**
```python
# File: backend/app/api/auth.py
@router.post("/register")
async def register(user_data: UserRegister):
    # 1. Validate email format (Pydantic)
    # 2. Check if user already exists
    existing_user = await database[db_name]["users"].find_one(
        {"email": user_data.email}
    )
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 3. Hash password
    hashed_password = pwd_context.hash(user_data.password)
    
    # 4. Create user document
    user_doc = {
        "_id": str(uuid4()),
        "name": user_data.name,
        "email": user_data.email,
        "password": hashed_password,
        "role": user_data.role,
        "created_at": datetime.utcnow(),
        "is_active": True,
        "face_descriptor": None
    }
    
    # 5. Insert into database
    await database[db_name]["users"].insert_one(user_doc)
    
    # 6. Initialize gamification stats
    stats_doc = {
        "_id": str(uuid4()),
        "user_id": user_doc["_id"],
        "xp": 0,
        "level": 1,
        "streak": 0,
        "badges": []
    }
    await database[db_name]["user_stats"].insert_one(stats_doc)
    
    return {"message": "User registered successfully", "user_id": user_doc["_id"]}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### Database Changes

**Users Collection:**
```json
{
  "_id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "John Doe",
  "email": "john@example.com",
  "password": "$2b$12$KqLwz...", // bcrypt hash
  "role": "student",
  "created_at": "2025-10-26T10:30:00Z",
  "is_active": true,
  "face_descriptor": null,
  "last_login": null
}
```

**User Stats Collection:**
```json
{
  "_id": "stats-550e8400-e29b-41d4-a716-446655440000",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "xp": 0,
  "level": 1,
  "streak": 0,
  "last_activity": null,
  "badges": [],
  "total_assessments": 0,
  "total_problems_solved": 0
}
```

---

### 2. User Login Flow

#### Process Diagram
```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   User UI    │         │   Frontend   │         │   Backend    │
│  (Login Page)│         │   Service    │         │   API        │
└──────┬───────┘         └──────┬───────┘         └──────┬───────┘
       │                        │                        │
       │ 1. Enter Credentials  │                        │
       │    (email, password)  │                        │
       │                        │                        │
       │ 2. Click Login        │                        │
       ├───────────────────────▶│                        │
       │                        │                        │
       │                        │ 3. POST /auth/login   │
       │                        │    {email, password}  │
       │                        ├───────────────────────▶│
       │                        │                        │
       │                        │                        │ 4. Find User by Email
       │                        │                        │    (MongoDB)
       │                        │                        ├────────┐
       │                        │                        │        │
       │                        │                        │◀───────┘
       │                        │                        │
       │                        │                        │ 5. Verify Password
       │                        │                        │    (bcrypt.verify)
       │                        │                        │
       │                        │                        │ 6. Create JWT Token
       │                        │                        │    {user_id, role,
       │                        │                        │     exp: 24h}
       │                        │                        │
       │                        │                        │ 7. Update last_login
       │                        │                        │    (MongoDB)
       │                        │                        │
       │                        │                        │ 8. Set HTTP-Only Cookie
       │                        │                        │    (access_token)
       │                        │                        │
       │                        │  9. Response          │
       │                        │     {user, token}     │
       │                        │◀───────────────────────┤
       │                        │                        │
       │ 10. Store Token       │                        │
       │     (localStorage)     │                        │
       │◀───────────────────────┤                        │
       │                        │                        │
       │ 11. Redirect to       │                        │
       │     Role Dashboard    │                        │
       │◀───────────────────────┤                        │
       │                        │                        │
       ▼                        ▼                        ▼
```

#### Files Involved

**Frontend:**
- `frontend/src/pages/Login.tsx` - Login page UI
- `frontend/src/api/authService.ts` - Authentication service
  - Function: `login(credentials: LoginCredentials)`
- `frontend/src/context/AuthContext.tsx` - Auth state management

**Backend:**
- `backend/app/api/auth.py` - Authentication endpoints
  - Endpoint: `POST /api/auth/login`
  - Function: `login(form_data: OAuth2PasswordRequestForm)`
- `backend/app/utils/security.py` - JWT token utilities
  - Function: `create_access_token(data: dict)`
  - Function: `verify_password(plain, hashed)`

#### Request Flow

**1. Frontend Login Request**
```typescript
// File: frontend/src/api/authService.ts
export const login = async (credentials: LoginCredentials) => {
  const response = await api.post('/auth/login', credentials);
  
  // Store token
  localStorage.setItem('access_token', response.data.access_token);
  
  // Update auth context
  setUser(response.data.user);
  
  return response.data;
};
```

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "SecurePassword123!"
}
```

**2. Backend Authentication**
```python
# File: backend/app/api/auth.py
@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # 1. Find user by email
    user = await database[db_name]["users"].find_one(
        {"email": form_data.username}  # OAuth2 uses 'username' field
    )
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
    
    # 2. Verify password
    if not pwd_context.verify(form_data.password, user["password"]):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
    
    # 3. Check if user is active
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=403,
            detail="Account is deactivated"
        )
    
    # 4. Create JWT token
    access_token = create_access_token(
        data={
            "sub": user["_id"],
            "email": user["email"],
            "role": user["role"]
        }
    )
    
    # 5. Update last login time
    await database[db_name]["users"].update_one(
        {"_id": user["_id"]},
        {"$set": {"last_login": datetime.utcnow()}}
    )
    
    # 6. Create response
    response = JSONResponse(content={
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user["_id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"]
        }
    })
    
    # 7. Set HTTP-only cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,  # HTTPS only
        samesite="lax",
        max_age=86400  # 24 hours
    )
    
    return response
```

**3. JWT Token Structure**
```python
# File: backend/app/utils/security.py
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    
    return encoded_jwt
```

**JWT Token Payload:**
```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "email": "john@example.com",
  "role": "student",
  "exp": 1730034600,
  "iat": 1729948200
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "John Doe",
    "email": "john@example.com",
    "role": "student"
  }
}
```

#### Role-Based Redirection

```typescript
// File: frontend/src/pages/Login.tsx
const handleLoginSuccess = (userData) => {
  switch (userData.role) {
    case 'student':
      navigate('/student/dashboard');
      break;
    case 'teacher':
      navigate('/teacher/dashboard');
      break;
    case 'admin':
      navigate('/admin/dashboard');
      break;
    default:
      navigate('/');
  }
};
```

---

## Face Recognition Authentication

### Feature Overview
Biometric authentication using facial recognition for secure, passwordless login.

### Technology Stack
- **Frontend:** face-api.js (TensorFlow.js based)
- **Backend:** face_recognition library (dlib based)
- **Models:** Face detection, landmark detection, face descriptor extraction

### 1. Face Registration Flow

#### Process Diagram
```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   User UI    │         │   Frontend   │         │   Backend    │
│  (Face       │         │   (face-api) │         │   API        │
│   Register)  │         │              │         │              │
└──────┬───────┘         └──────┬───────┘         └──────┬───────┘
       │                        │                        │
       │ 1. Request Camera     │                        │
       │    Access              │                        │
       ├───────────────────────▶│                        │
       │                        │                        │
       │ 2. Camera Stream ON   │                        │
       │◀───────────────────────┤                        │
       │                        │                        │
       │ 3. User Positions     │                        │
       │    Face in Frame      │                        │
       │                        │                        │
       │ 4. Capture Image      │                        │
       ├───────────────────────▶│                        │
       │                        │                        │
       │                        │ 5. Load Face Models   │
       │                        │    (tiny_face_detector,│
       │                        │     face_landmarks,    │
       │                        │     face_recognition)  │
       │                        │                        │
       │                        │ 6. Detect Face        │
       │                        │    in Image           │
       │                        ├────────┐              │
       │                        │        │              │
       │                        │◀───────┘              │
       │                        │                        │
       │                        │ 7. Extract Face       │
       │                        │    Descriptor         │
       │                        │    (128-dim vector)   │
       │                        │                        │
       │                        │ 8. POST /auth/        │
       │                        │    register-face      │
       │                        │    {user_id,          │
       │                        │     descriptor[]}     │
       │                        ├───────────────────────▶│
       │                        │                        │
       │                        │                        │ 9. Validate User
       │                        │                        │    (JWT token)
       │                        │                        │
       │                        │                        │ 10. Store Descriptor
       │                        │                        │     in User Document
       │                        │                        ├────────┐
       │                        │                        │        │
       │                        │                        │◀───────┘
       │                        │                        │
       │                        │  11. Response         │
       │                        │      {success: true}  │
       │                        │◀───────────────────────┤
       │                        │                        │
       │ 12. Show Success      │                        │
       │     Message            │                        │
       │◀───────────────────────┤                        │
       │                        │                        │
       ▼                        ▼                        ▼
```

#### Files Involved

**Frontend:**
- `frontend/src/pages/FaceRegister.tsx` - Face registration UI
- `frontend/src/utils/faceDetection.ts` - face-api.js utilities
- `frontend/src/api/authService.ts` - Auth service
  - Function: `registerFace(userId, descriptor)`

**Backend:**
- `backend/app/api/auth.py` - Authentication endpoints
  - Endpoint: `POST /api/auth/register-face`
  - Function: `register_face(face_data: FaceRegister)`
  - Endpoint: `GET /api/auth/face-status`

#### Implementation Details

**1. Frontend Face Detection**
```typescript
// File: frontend/src/utils/faceDetection.ts
import * as faceapi from 'face-api.js';

export const loadModels = async () => {
  const MODEL_URL = '/models';
  await faceapi.nets.tinyFaceDetector.loadFromUri(MODEL_URL);
  await faceapi.nets.faceLandmark68Net.loadFromUri(MODEL_URL);
  await faceapi.nets.faceRecognitionNet.loadFromUri(MODEL_URL);
};

export const detectFace = async (imageElement: HTMLImageElement) => {
  const detection = await faceapi
    .detectSingleFace(imageElement, new faceapi.TinyFaceDetectorOptions())
    .withFaceLandmarks()
    .withFaceDescriptor();
  
  if (!detection) {
    throw new Error('No face detected');
  }
  
  return detection.descriptor; // 128-dimensional Float32Array
};
```

**2. Face Registration Component**
```typescript
// File: frontend/src/pages/FaceRegister.tsx
const FaceRegister: React.FC = () => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [capturing, setCapturing] = useState(false);
  
  const startCamera = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { width: 640, height: 480 }
    });
    if (videoRef.current) {
      videoRef.current.srcObject = stream;
    }
  };
  
  const captureAndRegister = async () => {
    setCapturing(true);
    
    // Capture frame from video
    const canvas = document.createElement('canvas');
    const video = videoRef.current;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
    
    // Detect face
    const img = await faceapi.bufferToImage(canvas.toDataURL());
    const descriptor = await detectFace(img);
    
    // Send to backend
    await authService.registerFace(user.id, Array.from(descriptor));
    
    setCapturing(false);
    toast.success('Face registered successfully!');
  };
  
  return (
    <div>
      <video ref={videoRef} autoPlay />
      <button onClick={captureAndRegister}>Register Face</button>
    </div>
  );
};
```

**3. Backend Face Storage**
```python
# File: backend/app/api/auth.py
@router.post("/register-face")
async def register_face(
    face_data: FaceRegister,
    current_user: dict = Depends(get_current_user)
):
    # 1. Validate descriptor (must be 128 dimensions)
    if len(face_data.descriptor) != 128:
        raise HTTPException(
            status_code=400,
            detail="Invalid face descriptor"
        )
    
    # 2. Update user document with face descriptor
    result = await database[db_name]["users"].update_one(
        {"_id": current_user["_id"]},
        {"$set": {
            "face_descriptor": face_data.descriptor,
            "face_registered_at": datetime.utcnow()
        }}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=500,
            detail="Failed to register face"
        )
    
    return {"message": "Face registered successfully"}
```

### 2. Face Recognition Login Flow

#### Process Diagram
```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   User UI    │         │   Frontend   │         │   Backend    │
│  (Face Login)│         │   (face-api) │         │   API        │
└──────┬───────┘         └──────┬───────┘         └──────┬───────┘
       │                        │                        │
       │ 1. Enable Camera      │                        │
       ├───────────────────────▶│                        │
       │                        │                        │
       │ 2. Capture Image      │                        │
       ├───────────────────────▶│                        │
       │                        │                        │
       │                        │ 3. Extract Descriptor │
       │                        ├────────┐              │
       │                        │        │              │
       │                        │◀───────┘              │
       │                        │                        │
       │                        │ 4. POST /auth/face    │
       │                        │    {descriptor[]}     │
       │                        ├───────────────────────▶│
       │                        │                        │
       │                        │                        │ 5. Get All Users
       │                        │                        │    with Face Data
       │                        │                        ├────────┐
       │                        │                        │        │
       │                        │                        │◀───────┘
       │                        │                        │
       │                        │                        │ 6. Compare Descriptors
       │                        │                        │    (Euclidean distance)
       │                        │                        │    threshold: 0.6
       │                        │                        │
       │                        │                        │ 7. Find Best Match
       │                        │                        ├────────┐
       │                        │                        │        │
       │                        │                        │◀───────┘
       │                        │                        │
       │                        │                        │ 8. Generate JWT Token
       │                        │                        │    (if match found)
       │                        │                        │
       │                        │  9. Response          │
       │                        │     {token, user}     │
       │                        │◀───────────────────────┤
       │                        │                        │
       │ 10. Store Token &     │                        │
       │     Redirect           │                        │
       │◀───────────────────────┤                        │
       │                        │                        │
       ▼                        ▼                        ▼
```

#### Backend Face Matching Algorithm

```python
# File: backend/app/api/auth.py
import numpy as np

def calculate_distance(desc1: List[float], desc2: List[float]) -> float:
    """Calculate Euclidean distance between two face descriptors"""
    return np.linalg.norm(np.array(desc1) - np.array(desc2))

@router.post("/face")
async def face_login(face_data: FaceLogin):
    # 1. Get all users with face descriptors
    users = await database[db_name]["users"].find({
        "face_descriptor": {"$exists": True, "$ne": None}
    }).to_list(length=None)
    
    if not users:
        raise HTTPException(
            status_code=404,
            detail="No users with face recognition registered"
        )
    
    # 2. Find best match
    best_match = None
    best_distance = float('inf')
    THRESHOLD = 0.6  # Maximum distance for a match
    
    for user in users:
        distance = calculate_distance(
            face_data.descriptor,
            user["face_descriptor"]
        )
        
        if distance < best_distance and distance < THRESHOLD:
            best_distance = distance
            best_match = user
    
    # 3. Verify match found
    if not best_match:
        raise HTTPException(
            status_code=401,
            detail="Face not recognized"
        )
    
    # 4. Create JWT token
    access_token = create_access_token(
        data={
            "sub": best_match["_id"],
            "email": best_match["email"],
            "role": best_match["role"]
        }
    )
    
    # 5. Update last login
    await database[db_name]["users"].update_one(
        {"_id": best_match["_id"]},
        {"$set": {"last_login": datetime.utcnow()}}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": best_match["_id"],
            "name": best_match["name"],
            "email": best_match["email"],
            "role": best_match["role"]
        },
        "confidence": 1 - (best_distance / THRESHOLD)
    }
```

---

## Google OAuth Authentication

### Feature Overview
Social login integration with Google OAuth 2.0 for seamless authentication.

### OAuth 2.0 Flow

#### Process Diagram
```
┌────────────┐    ┌────────────┐    ┌────────────┐    ┌────────────┐
│   User     │    │  Frontend  │    │  Backend   │    │   Google   │
│            │    │            │    │            │    │   OAuth    │
└─────┬──────┘    └─────┬──────┘    └─────┬──────┘    └─────┬──────┘
      │                 │                  │                  │
      │ 1. Click        │                  │                  │
      │   "Login with   │                  │                  │
      │    Google"      │                  │                  │
      ├────────────────▶│                  │                  │
      │                 │                  │                  │
      │                 │ 2. GET /auth/    │                  │
      │                 │    google        │                  │
      │                 ├─────────────────▶│                  │
      │                 │                  │                  │
      │                 │                  │ 3. Redirect to   │
      │                 │                  │    Google OAuth  │
      │                 │                  │    (with client_id,│
      │                 │                  │     redirect_uri) │
      │                 │                  ├─────────────────▶│
      │                 │                  │                  │
      │ 4. Google Login Page              │                  │
      │◀──────────────────────────────────────────────────────┤
      │                 │                  │                  │
      │ 5. User         │                  │                  │
      │    Authenticates│                  │                  │
      │    & Grants     │                  │                  │
      │    Permissions  │                  │                  │
      ├──────────────────────────────────────────────────────▶│
      │                 │                  │                  │
      │                 │                  │ 6. Authorization │
      │                 │                  │    Code          │
      │                 │                  │◀─────────────────┤
      │                 │                  │                  │
      │                 │                  │ 7. Exchange Code │
      │                 │                  │    for Tokens    │
      │                 │                  ├─────────────────▶│
      │                 │                  │                  │
      │                 │                  │ 8. Access Token  │
      │                 │                  │    + User Info   │
      │                 │                  │◀─────────────────┤
      │                 │                  │                  │
      │                 │                  │ 9. Create/Update │
      │                 │                  │    User in DB    │
      │                 │                  ├────────┐         │
      │                 │                  │        │         │
      │                 │                  │◀───────┘         │
      │                 │                  │                  │
      │                 │                  │ 10. Generate JWT │
      │                 │                  │     Token        │
      │                 │                  │                  │
      │                 │ 11. Redirect to  │                  │
      │                 │     Frontend     │                  │
      │                 │     with Token   │                  │
      │                 │◀─────────────────┤                  │
      │                 │                  │                  │
      │ 12. Store Token │                  │                  │
      │     & Redirect  │                  │                  │
      │     to Dashboard│                  │                  │
      │◀────────────────┤                  │                  │
      │                 │                  │                  │
      ▼                 ▼                  ▼                  ▼
```

#### Files Involved

**Frontend:**
- `frontend/src/pages/Login.tsx` - Login page with Google button
- `frontend/src/config/oauth.ts` - OAuth configuration

**Backend:**
- `backend/app/api/auth.py` - OAuth endpoints
  - Endpoint: `GET /api/auth/google`
  - Endpoint: `GET /api/auth/google/callback`
- `backend/app/config.py` - Google OAuth credentials
- `.env` - Environment variables (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)

#### Implementation

**1. Frontend Google Login Button**
```typescript
// File: frontend/src/pages/Login.tsx
const GoogleLoginButton: React.FC = () => {
  const handleGoogleLogin = () => {
    // Redirect to backend OAuth endpoint
    window.location.href = `${API_BASE_URL}/auth/google`;
  };
  
  return (
    <button onClick={handleGoogleLogin} className="google-btn">
      <img src="/google-icon.svg" alt="Google" />
      Continue with Google
    </button>
  );
};
```

**2. Backend OAuth Initiation**
```python
# File: backend/app/api/auth.py
from authlib.integrations.starlette_client import OAuth

oauth = OAuth()
oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

@router.get("/google")
async def google_login(request: Request):
    # Generate redirect URI
    redirect_uri = request.url_for('google_callback')
    
    # Redirect to Google OAuth
    return await oauth.google.authorize_redirect(request, redirect_uri)
```

**3. OAuth Callback Handler**
```python
@router.get("/google/callback")
async def google_callback(request: Request):
    # 1. Get authorization token from Google
    token = await oauth.google.authorize_access_token(request)
    
    # 2. Get user info from Google
    user_info = token.get('userinfo')
    
    if not user_info:
        raise HTTPException(
            status_code=400,
            detail="Failed to get user info from Google"
        )
    
    # 3. Check if user exists
    user = await database[db_name]["users"].find_one({
        "email": user_info['email']
    })
    
    # 4. Create new user if doesn't exist
    if not user:
        user_doc = {
            "_id": str(uuid4()),
            "name": user_info['name'],
            "email": user_info['email'],
            "profile_picture": user_info.get('picture'),
            "role": "student",  # Default role
            "auth_provider": "google",
            "google_id": user_info['sub'],
            "created_at": datetime.utcnow(),
            "is_active": True
        }
        
        await database[db_name]["users"].insert_one(user_doc)
        
        # Initialize gamification
        await initialize_user_stats(user_doc["_id"])
        
        user = user_doc
    
    # 5. Update last login
    await database[db_name]["users"].update_one(
        {"_id": user["_id"]},
        {"$set": {"last_login": datetime.utcnow()}}
    )
    
    # 6. Create JWT token
    access_token = create_access_token(
        data={
            "sub": user["_id"],
            "email": user["email"],
            "role": user["role"]
        }
    )
    
    # 7. Redirect to frontend with token
    frontend_url = f"{FRONTEND_URL}/auth/callback?token={access_token}"
    return RedirectResponse(url=frontend_url)
```

**4. Frontend Callback Handler**
```typescript
// File: frontend/src/pages/AuthCallback.tsx
const AuthCallback: React.FC = () => {
  const navigate = useNavigate();
  const { setUser } = useAuth();
  
  useEffect(() => {
    const handleCallback = async () => {
      // Get token from URL
      const params = new URLSearchParams(window.location.search);
      const token = params.get('token');
      
      if (token) {
        // Store token
        localStorage.setItem('access_token', token);
        
        // Get user info
        const user = await authService.getCurrentUser();
        setUser(user);
        
        // Redirect based on role
        navigate(`/${user.role}/dashboard`);
      } else {
        navigate('/login');
      }
    };
    
    handleCallback();
  }, []);
  
  return <div>Completing login...</div>;
};
```

---

## Session Management

### JWT Token Management

#### Token Lifecycle
```
┌──────────────────────────────────────────────────────────────┐
│                      Token Lifecycle                         │
└──────────────────────────────────────────────────────────────┘

1. LOGIN
   ↓
[Generate JWT Token]
   - Payload: {user_id, role, email}
   - Expiry: 24 hours
   - Algorithm: HS256
   ↓
2. STORE TOKEN
   - localStorage: access_token
   - HTTP-only Cookie: access_token
   ↓
3. AUTHENTICATED REQUESTS
   ↓
[Include Token in Header]
   Authorization: Bearer <token>
   ↓
[Backend Validates Token]
   - Verify signature
   - Check expiry
   - Extract user info
   ↓
4a. TOKEN VALID          4b. TOKEN EXPIRED/INVALID
    ↓                        ↓
[Process Request]       [Return 401 Unauthorized]
                             ↓
                        [Frontend Redirects to Login]
                             ↓
                        [Clear Stored Token]
```

#### Token Validation Dependency

```python
# File: backend/app/api/auth.py
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Dependency to get current authenticated user from JWT token.
    Used in all protected endpoints.
    """
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 1. Decode JWT token
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        
        # 2. Extract user ID
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        # 3. Get user from database
        user = await database[db_name]["users"].find_one({"_id": user_id})
        
        if user is None:
            raise credentials_exception
        
        # 4. Check if user is active
        if not user.get("is_active", True):
            raise HTTPException(
                status_code=403,
                detail="User account is deactivated"
            )
        
        return user
        
    except JWTError:
        raise credentials_exception
```

#### Protected Endpoint Example

```python
@router.get("/protected-resource")
async def protected_resource(
    current_user: dict = Depends(get_current_user)
):
    """
    Any endpoint with current_user dependency requires authentication.
    The token is automatically extracted from Authorization header.
    """
    return {
        "message": "This is a protected resource",
        "user": current_user["name"]
    }
```

#### Frontend Request Interceptor

```typescript
// File: frontend/src/api/axios.ts
import axios from 'axios';

// Create axios instance
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
});

// Request interceptor - Add token to all requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - Handle token expiry
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

---

## Role-Based Access Control

### Role Hierarchy

```
┌─────────────────────────────────────────┐
│           ROLE HIERARCHY                │
└─────────────────────────────────────────┘

ADMIN (Highest Privileges)
  │
  ├─ Full platform control
  ├─ User management (all roles)
  ├─ System configuration
  ├─ Content moderation
  └─ Analytics access (all data)

TEACHER
  │
  ├─ Create & manage assessments
  ├─ Manage batches & students
  ├─ View student performance
  ├─ Generate reports
  └─ Access teaching analytics

STUDENT (Base Role)
  │
  ├─ Take assessments
  ├─ View own results
  ├─ Access learning materials
  ├─ Track personal progress
  └─ Practice coding
```

### Role-Based Authorization

#### Implementation

```python
# File: backend/app/dependencies/auth.py
from functools import wraps
from fastapi import HTTPException, Depends

def require_role(*allowed_roles: str):
    """
    Dependency factory for role-based authorization.
    Usage: current_user = Depends(require_role("teacher", "admin"))
    """
    async def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
            )
        return current_user
    
    return role_checker
```

#### Usage in Endpoints

```python
# File: backend/app/api/teacher.py

# Only teachers and admins can access
@router.get("/dashboard")
async def teacher_dashboard(
    current_user: dict = Depends(require_role("teacher", "admin"))
):
    # Teacher-specific logic
    pass

# Only admins can access
@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: dict = Depends(require_role("admin"))
):
    # Admin-only logic
    pass

# Any authenticated user can access
@router.get("/profile")
async def get_profile(
    current_user: dict = Depends(get_current_user)
):
    # Available to all authenticated users
    pass
```

#### Frontend Route Protection

```typescript
// File: frontend/src/components/ProtectedRoute.tsx
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles: string[];
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  allowedRoles
}) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return <LoadingSpinner />;
  }
  
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  
  if (!allowedRoles.includes(user.role)) {
    return <Navigate to="/unauthorized" replace />;
  }
  
  return <>{children}</>;
};

// Usage in App.tsx
<Route
  path="/teacher/*"
  element={
    <ProtectedRoute allowedRoles={['teacher', 'admin']}>
      <TeacherDashboard />
    </ProtectedRoute>
  }
/>
```

---

## User Profile Management

### Get Current User

#### Endpoint Flow
```
Frontend                    Backend                   Database
   │                           │                         │
   │ GET /auth/status         │                         │
   │ Authorization: Bearer... │                         │
   ├─────────────────────────▶│                         │
   │                           │                         │
   │                           │ 1. Validate JWT        │
   │                           ├──────────┐             │
   │                           │          │             │
   │                           │◀─────────┘             │
   │                           │                         │
   │                           │ 2. Get User from DB    │
   │                           ├────────────────────────▶│
   │                           │                         │
   │                           │ User Document           │
   │                           │◀────────────────────────┤
   │                           │                         │
   │ User Data (sanitized)    │                         │
   │◀─────────────────────────┤                         │
   │                           │                         │
```

```python
@router.get("/status")
async def get_status(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user's information"""
    return {
        "authenticated": True,
        "user": {
            "id": current_user["_id"],
            "name": current_user["name"],
            "email": current_user["email"],
            "role": current_user["role"],
            "profile_picture": current_user.get("profile_picture"),
            "created_at": current_user["created_at"]
        }
    }
```

### Update User Profile

```python
@router.put("/users/me")
async def update_profile(
    update_data: UserProfileUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update current user's profile"""
    
    # Allowed fields to update
    allowed_fields = {"name", "profile_picture", "bio", "phone"}
    update_dict = {
        k: v for k, v in update_data.dict(exclude_unset=True).items()
        if k in allowed_fields
    }
    
    if not update_dict:
        raise HTTPException(400, "No valid fields to update")
    
    # Update user
    result = await database[db_name]["users"].update_one(
        {"_id": current_user["_id"]},
        {"$set": update_dict}
    )
    
    return {"message": "Profile updated successfully"}
```

### Logout

```python
@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """Logout user (client-side token removal mainly)"""
    
    # Optionally: Store token in blacklist for added security
    # For now, just confirm logout
    
    response = JSONResponse(content={"message": "Logged out successfully"})
    response.delete_cookie("access_token")
    
    return response
```

```typescript
// Frontend logout
const logout = async () => {
  try {
    await authService.logout();
  } finally {
    localStorage.removeItem('access_token');
    setUser(null);
    navigate('/login');
  }
};
```

---

## Summary

### Authentication Features Matrix

| Feature | Complexity | Security Level | Files Involved |
|---------|-----------|---------------|----------------|
| Email/Password | Medium | High (bcrypt + JWT) | 4 frontend, 3 backend |
| Face Recognition | High | Very High (biometric) | 5 frontend, 3 backend |
| Google OAuth | High | Very High (OAuth 2.0) | 3 frontend, 3 backend |
| Session Management | Medium | High (JWT) | 2 frontend, 2 backend |
| RBAC | Medium | High | 3 frontend, 4 backend |

### Key Security Measures

1. **Password Security**
   - bcrypt hashing (cost factor: 12)
   - No plain text storage
   - Validation on both frontend and backend

2. **Token Security**
   - JWT with 24-hour expiry
   - HTTP-only cookies
   - Secure flag for HTTPS
   - Token validation on every request

3. **Authorization**
   - Role-based access control
   - Dependency injection for auth checks
   - Frontend route protection

4. **Biometric Security**
   - 128-dimensional face descriptors
   - Euclidean distance threshold: 0.6
   - Server-side matching only

---

**[Back to Features Overview](./FEATURES_OVERVIEW.md)** | **[Next: Assessment Features →](./ASSESSMENT_FEATURES.md)**

