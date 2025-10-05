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
    name: Optional[str] = None
    profile_picture: Optional[str] = None
    google_id: Optional[str] = None

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

class FaceLoginRequest(BaseModel):
    face_image: str  # Base64 encoded image
    user_id: Optional[str] = None

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
    questions: List[QuestionCreate] = []
    max_attempts: int = Field(default=1, ge=1, le=10)
    type: str = Field(default="mcq")

class AssessmentResponse(BaseModel):
    id: str
    title: str
    description: str
    subject: str
    difficulty: DifficultyLevel
    time_limit: int
    max_attempts: int
    question_count: int
    created_by: str
    created_at: str
    status: str
    type: str
    is_active: bool
    total_questions: int

class QuestionResponse(BaseModel):
    id: str
    question: str
    options: List[str]
    correct_answer: int
    explanation: Optional[str] = None
    points: int = 1

class CodingQuestionCreate(BaseModel):
    title: str
    description: str
    problem_statement: str
    constraints: List[str]
    examples: List[Dict[str, Any]]
    test_cases: List[Dict[str, Any]]
    hidden_test_cases: List[Dict[str, Any]]
    expected_complexity: str
    hints: List[str]
    points: int = 10
    time_limit: int = 30
    memory_limit: int = 128

class CodingQuestionResponse(BaseModel):
    id: str
    title: str
    description: str
    problem_statement: str
    constraints: List[str]
    examples: List[Dict[str, Any]]
    hints: List[str]
    points: int
    time_limit: int
    memory_limit: int
    test_cases: List[Dict[str, Any]]

class CodingSubmission(BaseModel):
    question_id: str
    code: str
    language: str

class CodingSubmissionResponse(BaseModel):
    id: str
    assessment_id: str
    question_id: str
    status: str
    execution_time: int
    memory_used: int
    test_results: List[Dict[str, Any]]
    score: int
    max_score: int
    submitted_at: str

class AssessmentSubmission(BaseModel):
    answers: List[int]
    time_taken: int

class AssessmentResult(BaseModel):
    id: str
    assessment_id: str
    student_id: str
    student_name: str
    score: float
    total_questions: int
    percentage: float
    time_taken: int
    submitted_at: str
    attempt_number: int

class LeaderboardEntry(BaseModel):
    student_id: str
    student_name: str
    score: float
    percentage: float
    time_taken: Optional[int] = None
    rank: int

class AssessmentLeaderboard(BaseModel):
    assessment_id: str
    assessment_title: str
    total_students: int
    leaderboard: List[LeaderboardEntry]

class StudentNotification(BaseModel):
    id: str
    student_id: str
    type: str
    title: str
    message: str
    assessment_id: Optional[str] = None
    created_at: str
    is_read: bool

# Coding Schemas
class CodingProblemCreate(BaseModel):
    title: str
    description: str

class CodingSolutionSubmit(BaseModel):
    problem_id: str
    code: str
    language: str

class CodingSolutionResponse(BaseModel):
    id: str
    problem_id: str
    student_id: str
    code: str
    language: str
    status: str
    execution_time: int
    memory_used: int
    test_results: List[Dict[str, Any]]
    score: int
    max_score: int
    submitted_at: datetime

class CodeExecutionRequest(BaseModel):
    code: str
    language: str
    test_cases: List[Dict[str, Any]]

class CodeExecutionResponse(BaseModel):
    status: str
    execution_time: int
    memory_used: int
    test_results: List[Dict[str, Any]]
    output: str
    error: Optional[str] = None

class CodingSessionStart(BaseModel):
    problem_id: str
    language: str

class CodingSessionUpdate(BaseModel):
    session_id: str
    code: str
    cursor_position: int

class CodingAnalyticsResponse(BaseModel):
    total_problems: int
    solved_problems: int
    average_time: float
    success_rate: float
    language_stats: Dict[str, int]

class AIFeedbackRequest(BaseModel):
    code: str
    problem_description: str
    language: str

class ProblemGenerationRequest(BaseModel):
    topic: str
    difficulty: str
    language: str
    count: int = 1

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
    type: str = Field(..., pattern="^(info|warning|success|error)$")
    target_users: Optional[List[str]] = None
    priority: str = Field("normal", pattern="^(low|normal|high|urgent)$")

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