from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
import bcrypt

class PyObjectId(ObjectId):
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

# User Model
class UserModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    username: Optional[str] = None
    email: EmailStr
    password: Optional[str] = None
    is_admin: bool = False
    role: str = "student"  # Added role field with default value
    google_id: Optional[str] = None
    name: Optional[str] = None
    profile_picture: Optional[str] = None
    face_descriptor: Optional[List[float]] = None
    
    # Gamification fields
    xp: int = 0  # Experience points
    level: int = 1  # User level
    streak: int = 0  # Current streak
    longest_streak: int = 0  # Longest streak achieved
    badges: List[str] = []  # List of earned badges
    last_activity: Optional[datetime] = None  # Last activity timestamp
    total_questions_answered: int = 0  # Total questions answered
    correct_answers: int = 0  # Total correct answers
    perfect_scores: int = 0  # Number of perfect scores (100%)
    consecutive_days: int = 0  # Consecutive days of activity

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "password": "hashed_password",
                "is_admin": False,
                "google_id": "google_oauth_id",
                "name": "John Doe",
                "profile_picture": "https://example.com/picture.jpg",
                "face_descriptor": [0.1, 0.2, 0.3],
                "xp": 150,
                "level": 3,
                "streak": 5,
                "longest_streak": 10,
                "badges": ["first_quiz", "perfect_score"],
                "total_questions_answered": 50,
                "correct_answers": 45,
                "perfect_scores": 2,
                "consecutive_days": 5
            }
        }
    )

    @classmethod
    def hash_password(cls, password: str) -> str:
        """Hash password using bcrypt"""
        try:
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception as e:
            print(f"❌ [PASSWORD] Hashing failed: {str(e)}")
            raise Exception(f"Password hashing failed: {str(e)}")

    @classmethod
    def verify_password(cls, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# Question Model
class QuestionModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    topic: str
    difficulty: str
    question: str
    answer: str
    options: List[str]

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "topic": "JavaScript",
                "difficulty": "medium",
                "question": "What is the output of console.log(typeof null)?",
                "answer": "object",
                "options": ["null", "object", "undefined", "number"]
            }
        }
    )

# Coding Problem Model
class CodingProblemModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    title: str
    description: str
    topic: str
    difficulty: str
    constraints: List[str]
    examples: List[Dict[str, Any]]
    test_cases: List[Dict[str, Any]]
    hidden_test_cases: List[Dict[str, Any]]
    expected_complexity: Dict[str, str]  # time and space complexity
    hints: List[str]
    created_by: str  # "AI" or user_id
    created_at: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str]
    success_rate: float = 0.0
    average_time: Optional[int] = None  # in seconds

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "title": "Two Sum",
                "description": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
                "topic": "Arrays",
                "difficulty": "easy",
                "constraints": ["2 <= nums.length <= 10^4", "-10^9 <= nums[i] <= 10^9"],
                "examples": [
                    {
                        "input": "nums = [2,7,11,15], target = 9",
                        "output": "[0,1]",
                        "explanation": "Because nums[0] + nums[1] == 9, we return [0, 1]."
                    }
                ],
                "test_cases": [
                    {"input": {"nums": [2, 7, 11, 15], "target": 9}, "output": [0, 1]},
                    {"input": {"nums": [3, 2, 4], "target": 6}, "output": [1, 2]}
                ],
                "expected_complexity": {"time": "O(n)", "space": "O(n)"},
                "hints": ["Use a hash map to store numbers and their indices"],
                "tags": ["hash-table", "array"]
            }
        }
    )

# Coding Solution Model
class CodingSolutionModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    problem_id: PyObjectId
    code: str
    language: str
    status: str  # "accepted", "wrong_answer", "time_limit_exceeded", "runtime_error", "compilation_error"
    execution_time: Optional[int] = None  # in milliseconds
    memory_used: Optional[int] = None  # in KB
    test_results: List[Dict[str, Any]]
    ai_feedback: Optional[Dict[str, Any]] = None
    code_quality_score: Optional[float] = None
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    attempts: int = 1

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str}
    )

# Coding Session Model
class CodingSessionModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    problem_id: PyObjectId
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    total_time: Optional[int] = None  # in seconds
    keystrokes: Optional[int] = None
    lines_of_code: Optional[int] = None
    compilation_attempts: int = 0
    test_runs: int = 0
    hints_used: int = 0
    final_status: Optional[str] = None
    session_data: Optional[Dict[str, Any]] = None  # for storing additional session info

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str}
    )

# Coding Analytics Model
class CodingAnalyticsModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    total_problems_solved: int = 0
    total_problems_attempted: int = 0
    success_rate: float = 0.0
    average_time_per_problem: float = 0.0
    preferred_language: Optional[str] = None
    skill_level: str = "beginner"  # beginner, intermediate, advanced, expert
    strong_topics: List[str] = []
    weak_topics: List[str] = []
    improvement_areas: List[str] = []
    learning_path: List[Dict[str, Any]] = []
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    coding_streak: int = 0
    longest_streak: int = 0
    problems_by_difficulty: Dict[str, int] = {"easy": 0, "medium": 0, "hard": 0}
    problems_by_topic: Dict[str, int] = {}

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str}
    )

# Result Model
class ResultModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    score: int
    total_questions: int
    questions: List[Dict[str, Any]]
    user_answers: List[str]
    date: datetime = Field(default_factory=datetime.utcnow)
    topic: str
    difficulty: str
    time_taken: Optional[int] = None  # Time taken in seconds
    explanations: Optional[List[Dict[str, Any]]] = None  # AI explanations for questions
    correct_answers: Optional[int] = None
    incorrect_answers: Optional[int] = None
    percentage: Optional[float] = None

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "user_id": "507f1f77bcf86cd799439011",
                "score": 8,
                "total_questions": 10,
                "questions": [
                    {
                        "question": "What is JavaScript?",
                        "options": ["Programming language", "Markup language", "Style sheet", "Database"],
                        "answer": "Programming language"
                    }
                ],
                "user_answers": ["Programming language"],
                "topic": "JavaScript",
                "difficulty": "easy",
                "time_taken": 540,
                "explanations": [
                    {
                        "questionIndex": 0,
                        "explanation": "JavaScript is a programming language used for web development."
                    }
                ],
                "correct_answers": 8,
                "incorrect_answers": 2,
                "percentage": 80.0
            }
        }
    )

# Badge Model
class BadgeModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str
    description: str
    icon: str
    xp_reward: int
    criteria: Dict[str, Any]  # Conditions to earn the badge
    category: str  # "achievement", "streak", "performance", "participation"
    rarity: str = "common"  # "common", "rare", "epic", "legendary"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str}
    )

# Learning Path Model
class LearningPathModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    current_skill_assessment: Dict[str, Any]
    learning_objectives: List[Dict[str, Any]]
    recommended_topics: List[Dict[str, Any]]
    practice_schedule: Dict[str, Any]
    improvement_areas: List[Dict[str, Any]]
    milestone_tracking: List[Dict[str, Any]]
    ai_generated: bool = True
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str}
    )

# Batch Model
class BatchModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str
    description: Optional[str] = None
    teacher_id: PyObjectId
    student_ids: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    settings: Dict[str, Any] = {}

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str}
    )

# Batch Analytics Model
class BatchAnalyticsModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    batch_id: PyObjectId
    total_students: int
    average_score: float
    completion_rate: float
    struggling_students: List[Dict[str, Any]]
    top_performers: List[Dict[str, Any]]
    recent_activities: List[Dict[str, Any]]
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str}
    )

# AI Student Report Model
class AIStudentReportModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    student_id: PyObjectId
    teacher_id: PyObjectId
    report_content: str
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    performance_summary: Dict[str, Any]
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str}
    )

# Platform Metrics Model
class PlatformMetricsModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    date: datetime = Field(default_factory=datetime.utcnow)
    daily_active_users: int
    monthly_active_users: int
    user_engagement_ratio: float
    assessment_completion_rate: float
    feature_adoption: Dict[str, Any]
    content_quality_score: float
    system_health_score: float

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str}
    )

# Content Quality Model
class ContentQualityModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    content_id: str  # ID of question or coding problem
    content_type: str  # "question" or "coding_problem"
    success_rate: float
    failure_rate: float
    flagged_reason: Optional[str] = None
    ai_audit_score: Optional[float] = None
    ai_audit_feedback: Optional[str] = None
    last_audited: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str}
    )

# Teacher Performance Model
class TeacherPerformanceModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    teacher_id: PyObjectId
    student_performance_score: float
    content_contribution_score: float
    engagement_score: float
    total_assessments_created: int
    total_questions_created: int
    average_student_score: float
    student_satisfaction_score: float
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str}
    ) 