"""
Pydantic schemas for request/response validation
Contains all API request and response models
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from enum import Enum

class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, validation_info=None):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")

# Enums
class UserRole(str, Enum):
    student = "student"
    teacher = "teacher"
    admin = "admin"

class DifficultyLevel(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    role: UserRole = UserRole.student

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    profile_picture: Optional[str] = None

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    profile_picture: Optional[str] = None
    bio: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None

class UserResponse(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    profile_picture: Optional[str] = None
    bio: Optional[str] = None
    xp: int = 0
    level: int = 1
    badges: List[str] = []
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str}
    )

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserSettings(BaseModel):
    notifications: bool = True
    email_updates: bool = True
    theme: str = "light"
    language: str = "en"

class SettingsResponse(BaseModel):
    settings: UserSettings
    updated_at: datetime

# Assessment Schemas
class AssessmentConfig(BaseModel):
    topic: str
    qnCount: int = Field(..., ge=1, le=50)
    difficulty: DifficultyLevel

class QuestionCreate(BaseModel):
    question: str
    options: List[str]
    correct_answer: int
    explanation: Optional[str] = None
    difficulty: DifficultyLevel = DifficultyLevel.medium

class AssessmentCreate(BaseModel):
    title: str
    description: str
    subject: str
    difficulty: DifficultyLevel
    time_limit: int = Field(..., ge=1, le=300)
    questions: List[QuestionCreate]

class AssessmentResponse(BaseModel):
    id: str
    title: str
    description: str
    subject: str
    difficulty: DifficultyLevel
    time_limit: int
    created_by: str
    created_at: datetime
    is_active: bool
    total_questions: int

# Coding Schemas
class CodingProblemCreate(BaseModel):
    title: str
    description: str
    difficulty: DifficultyLevel
    language: str
    test_cases: List[Dict[str, Any]]
    starter_code: str
    hints: Optional[List[str]] = None

class CodingProblemResponse(BaseModel):
    id: str
    title: str
    description: str
    difficulty: DifficultyLevel
    language: str
    test_cases: List[Dict[str, Any]]
    starter_code: str
    hints: Optional[List[str]] = None
    created_at: datetime
    is_active: bool

class CodeSubmission(BaseModel):
    problem_id: str
    code: str
    language: str

class CodeExecutionResult(BaseModel):
    submission_id: str
    problem_id: str
    student_id: str
    code: str
    language: str
    test_results: List[Dict[str, Any]]
    passed_tests: int
    total_tests: int
    execution_time: float
    memory_usage: float
    status: str
    submitted_at: datetime

# Notification Schemas
class NotificationCreate(BaseModel):
    title: str
    message: str
    type: str = Field(..., regex="^(info|warning|success|error)$")
    target_users: Optional[List[str]] = None
    priority: str = Field("normal", regex="^(low|normal|high|urgent)$")

class NotificationResponse(BaseModel):
    id: str
    title: str
    message: str
    type: str
    priority: str
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime] = None

# Analytics Schemas
class UserStats(BaseModel):
    total_users: int
    active_users: int
    new_users_today: int
    users_by_role: Dict[str, int]

class PlatformStats(BaseModel):
    total_users: int
    active_users: int
    total_teachers: int
    total_students: int
    total_assessments: int
    total_coding_problems: int
    platform_health: str

class StudentPerformance(BaseModel):
    student_id: str
    student_name: str
    overall_score: float
    assignments_completed: int
    assignments_total: int
    last_activity: Optional[datetime]
    performance_trend: str
    strengths: List[str]
    weaknesses: List[str]

# Response Schemas
class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int