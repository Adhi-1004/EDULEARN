from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import List, Optional, Dict, Any, Annotated
from datetime import datetime
from bson import ObjectId

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

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: Optional[str] = None
    name: Optional[str] = None
    profile_picture: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    google_id: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    is_admin: bool = False
    google_id: Optional[str] = None
    face_descriptor: Optional[List[float]] = None

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str}
    )

class FaceLoginRequest(BaseModel):
    face_descriptor: List[float]

# Question schemas
class QuestionBase(BaseModel):
    topic: str
    difficulty: str
    question: str
    answer: str
    options: List[str]
    explanation: Optional[str] = None

class QuestionCreate(QuestionBase):
    pass

class QuestionResponse(QuestionBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str}
    )

# Result schemas
class ResultBase(BaseModel):
    user_id: str  # Changed from PyObjectId to str for easier frontend integration
    score: int
    total_questions: int
    questions: List[Dict[str, Any]]
    user_answers: List[str]
    topic: str
    difficulty: str
    time_taken: Optional[int] = None  # Time taken in seconds
    explanations: Optional[List[Dict[str, Any]]] = None  # AI explanations for questions

class ResultCreate(ResultBase):
    pass

class ResultResponse(ResultBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    date: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str}
    )

# Detailed result schemas for comprehensive test history
class DetailedResult(BaseModel):
    id: str
    user_id: str
    score: int
    total_questions: int
    questions: List[Dict[str, Any]]
    user_answers: List[str]
    topic: str
    difficulty: str
    time_taken: Optional[int] = None
    explanations: Optional[List[Dict[str, Any]]] = None
    date: datetime
    percentage: float
    correct_answers: int
    incorrect_answers: int

class TestHistoryItem(BaseModel):
    id: str
    score: int
    total_questions: int
    topic: str
    difficulty: str
    date: str
    percentage: float
    time_taken: Optional[int] = None

class QuestionReview(BaseModel):
    question_index: int
    question: str
    options: List[str]
    correct_answer: str
    user_answer: str
    is_correct: bool
    explanation: Optional[str] = None

class DetailedResultResponse(BaseModel):
    success: bool
    result: DetailedResult
    question_reviews: List[QuestionReview]

# Assessment schemas
class AssessmentConfig(BaseModel):
    topic: str = Field(..., min_length=1)
    qnCount: int = Field(..., ge=1, le=50, alias="qn_count")
    difficulty: str = Field(..., pattern="^(easy|medium|hard|Easy|Medium|Hard|Very Easy|Very Hard)$")

    model_config = ConfigDict(populate_by_name=True)
    
    def __init__(self, **data):
        super().__init__(**data)
        # Convert difficulty to lowercase for consistency
        if hasattr(self, 'difficulty'):
            self.difficulty = self.difficulty.lower()

# Google OAuth schemas
class GoogleAuthRequest(BaseModel):
    code: str
    redirect_uri: str

# Session schemas
class SessionData(BaseModel):
    user_id: str
    email: str
    name: Optional[str] = None
    profile_picture: Optional[str] = None

# Coding Platform schemas
class CodingProblemCreate(BaseModel):
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=10)
    topic: str
    difficulty: str = Field(..., pattern="^(easy|medium|hard)$")
    constraints: List[str]
    examples: List[Dict[str, Any]]
    test_cases: List[Dict[str, Any]]
    hidden_test_cases: List[Dict[str, Any]]
    expected_complexity: Dict[str, str]
    hints: List[str] = []
    tags: List[str] = []

class CodingProblemResponse(BaseModel):
    id: str
    title: str
    description: str
    topic: str
    difficulty: str
    constraints: List[str]
    examples: List[Dict[str, Any]]
    hints: List[str]
    tags: List[str]
    success_rate: float
    average_time: Optional[int] = None

    model_config = ConfigDict(populate_by_name=True)

class CodingSolutionSubmit(BaseModel):
    problem_id: str
    code: str
    language: str = Field(..., pattern="^(python|javascript|java|cpp|go)$")

class CodingSolutionResponse(BaseModel):
    id: str
    problem_id: str
    status: str
    execution_time: Optional[int] = None
    memory_used: Optional[int] = None
    test_results: List[Dict[str, Any]]
    ai_feedback: Optional[Dict[str, Any]] = None
    code_quality_score: Optional[float] = None
    submitted_at: str

    model_config = ConfigDict(populate_by_name=True)

class CodeExecutionRequest(BaseModel):
    code: str
    language: str
    test_cases: List[Dict[str, Any]]
    time_limit: int = 5000  # milliseconds
    memory_limit: int = 256  # MB
    timeout: int = 10  # seconds
    use_judge0: bool = False

class CodeExecutionResponse(BaseModel):
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    results: Optional[List[Dict[str, Any]]] = None
    execution_time: Optional[int] = None
    memory_used: Optional[int] = None
    passed_tests: Optional[int] = None
    total_tests: Optional[int] = None
    success_rate: Optional[float] = None

class CodingSessionStart(BaseModel):
    problem_id: str

class CodingSessionUpdate(BaseModel):
    session_id: str
    keystrokes: Optional[int] = None
    lines_of_code: Optional[int] = None
    compilation_attempts: Optional[int] = None
    test_runs: Optional[int] = None
    hints_used: Optional[int] = None

class CodingAnalyticsResponse(BaseModel):
    total_problems_solved: int
    total_problems_attempted: int
    success_rate: float
    average_time_per_problem: float
    preferred_language: Optional[str]
    skill_level: str
    strong_topics: List[str]
    weak_topics: List[str]
    improvement_areas: List[str]
    learning_path: List[Dict[str, Any]]
    coding_streak: int
    longest_streak: int
    problems_by_difficulty: Dict[str, int]
    problems_by_topic: Dict[str, int]

class AIFeedbackRequest(BaseModel):
    code: str
    problem_description: str
    language: str
    test_results: List[Dict[str, Any]]

class ProblemGenerationRequest(BaseModel):
    topic: str
    difficulty: str
    user_skill_level: str = "intermediate"
    focus_areas: List[str] = []
    avoid_topics: List[str] = []
    timestamp: Optional[int] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None

# Settings schemas
class UserSettings(BaseModel):
    userId: str
    theme: Dict[str, str]
    notifications: Dict[str, bool]
    privacy: Dict[str, bool]

class SettingsResponse(BaseModel):
    success: bool
    message: str 