"""
Database models and schemas
Contains all MongoDB document models and Pydantic schemas
"""
from pydantic import BaseModel, Field, EmailStr, ConfigDict
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

class NotificationType(str, Enum):
    info = "info"
    warning = "warning"
    success = "success"
    error = "error"

class NotificationPriority(str, Enum):
    low = "low"
    normal = "normal"
    high = "high"
    urgent = "urgent"

# User Model
class UserModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    username: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.student
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    # Gamification fields
    xp: int = 0
    level: int = 1
    streak: int = 0
    longest_streak: int = 0
    badges: List[str] = []
    last_activity: Optional[datetime] = None
    
    # Learning analytics
    total_questions_answered: int = 0
    correct_answers: int = 0
    average_score: float = 0.0
    
    # Profile information
    profile_picture: Optional[str] = None
    bio: Optional[str] = None
    preferences: Dict[str, Any] = {}
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

# Assessment Model
class AssessmentModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    title: str
    description: str
    subject: str
    difficulty: DifficultyLevel
    time_limit: int  # minutes
    questions: List[Dict[str, Any]]
    created_by: str  # User ID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    is_active: bool = True
    total_questions: int
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

# Coding Problem Model
class CodingProblemModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    title: str
    description: str
    difficulty: DifficultyLevel
    language: str
    test_cases: List[Dict[str, Any]]
    starter_code: str
    hints: List[str] = []
    created_by: str  # User ID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    is_active: bool = True
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

# Notification Model
class NotificationModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    title: str
    message: str
    type: NotificationType
    priority: NotificationPriority = NotificationPriority.normal
    is_read: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    read_at: Optional[datetime] = None
    created_by: Optional[str] = None
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

# Assessment Submission Model
class AssessmentSubmissionModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    assessment_id: str
    student_id: str
    answers: List[Dict[str, Any]]
    score: float
    total_questions: int
    correct_answers: int
    time_taken: int  # seconds
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

# Code Submission Model
class CodeSubmissionModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
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
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )