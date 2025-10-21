"""
Database models and schemas
Contains all MongoDB document models and Pydantic schemas
"""
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from enum import Enum
import bcrypt

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
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        return {"type": "string"}

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
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    username: str
    email: EmailStr
    password_hash: str
    role: UserRole = UserRole.student
    profile_picture: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    settings: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

# Assessment Model
class AssessmentModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    title: str
    description: str
    subject: str
    difficulty: DifficultyLevel
    time_limit: int
    questions: List[Dict[str, Any]]
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    total_questions: int

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

# Notification Model
class NotificationModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: str
    type: NotificationType
    title: str
    message: str
    priority: NotificationPriority = NotificationPriority.normal
    is_read: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    read_at: Optional[datetime] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

# Coding Models
class CodingProblemModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    title: str
    description: str
    difficulty: DifficultyLevel
    language: str
    test_cases: List[Dict[str, Any]]
    starter_code: str
    hints: Optional[List[str]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    is_active: bool = True

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class CodingSolutionModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
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
    submitted_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class CodingSessionModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    problem_id: str
    student_id: str
    language: str
    code: str
    cursor_position: int = 0
    started_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class CodingAnalyticsModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    student_id: str
    total_problems: int = 0
    solved_problems: int = 0
    average_time: float = 0.0
    success_rate: float = 0.0
    language_stats: Dict[str, int] = {}
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )