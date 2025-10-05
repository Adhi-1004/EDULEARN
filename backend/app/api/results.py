"""
Results endpoints
Handles test results and user performance data
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

from ..db import get_db
from ..models.models import UserModel
from ..dependencies import get_current_user

router = APIRouter()

# Response Models
class TestResult(BaseModel):
    id: str
    test_name: str
    score: float
    total_questions: int
    correct_answers: int
    completed_at: datetime
    duration: int  # in seconds

class UserResultsResponse(BaseModel):
    success: bool
    results: List[TestResult]
    total: int

@router.get("/user/{user_id}", response_model=UserResultsResponse)
async def get_user_results(
    user_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """Get user's test results"""
    try:
        # Verify user can access this data
        if current_user.id != user_id and current_user.role not in ["admin", "teacher"]:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to access this user's results"
            )
        
        db = await get_db()
        
        # For now, return mock data
        # In a real implementation, this would query the database
        mock_results = [
            TestResult(
                id="1",
                test_name="Python Basics",
                score=85.0,
                total_questions=10,
                correct_answers=8,
                completed_at=datetime.utcnow(),
                duration=1200
            ),
            TestResult(
                id="2", 
                test_name="Data Structures",
                score=92.0,
                total_questions=15,
                correct_answers=14,
                completed_at=datetime.utcnow(),
                duration=1800
            )
        ]
        
        return UserResultsResponse(
            success=True,
            results=mock_results,
            total=len(mock_results)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get user results: {str(e)}"
        )

@router.get("/analytics/{user_id}")
async def get_user_analytics(
    user_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """Get user analytics data"""
    try:
        # Verify user can access this data
        if current_user.id != user_id and current_user.role not in ["admin", "teacher"]:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to access this user's analytics"
            )
        
        # Return mock analytics data
        analytics_data = {
            "success": True,
            "analytics": {
                "total_tests": 5,
                "average_score": 78.5,
                "total_time_spent": 3600,  # seconds
                "streak_days": 7,
                "improvement_rate": 12.5,
                "strongest_subject": "Python",
                "weakest_subject": "Algorithms",
                "recent_performance": [
                    {"date": "2024-01-01", "score": 85},
                    {"date": "2024-01-02", "score": 78},
                    {"date": "2024-01-03", "score": 92}
                ]
            }
        }
        
        return analytics_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get user analytics: {str(e)}"
        )

# Request Models
class AssessmentSubmission(BaseModel):
    user_id: str
    score: float
    total_questions: int
    questions: List[Dict[str, Any]]  # List of questions
    user_answers: List[str]  # List of user answers
    topic: str
    difficulty: str
    time_taken: int  # in seconds
    explanations: Optional[List[Dict[str, Any]]] = []  # Optional explanations
    test_name: Optional[str] = None  # Optional test name
    answers: Optional[List[Dict[str, Any]]] = None  # Optional answers format
    time_spent: Optional[int] = None  # Optional time_spent format

class SubmissionResponse(BaseModel):
    success: bool
    score: float
    correct_answers: int
    total_questions: int
    message: str

@router.post("", response_model=SubmissionResponse)
@router.post("/", response_model=SubmissionResponse)
async def submit_assessment_result(
    submission: AssessmentSubmission,
    current_user: UserModel = Depends(get_current_user)
):
    """Submit assessment results"""
    try:
        print(f"🔍 [RESULTS] Received submission: {submission}")
        print(f"🔍 [RESULTS] Submission type: {type(submission)}")
        print(f"🔍 [RESULTS] Submission dict: {submission.__dict__ if hasattr(submission, '__dict__') else 'No dict'}")
        # Calculate score based on user answers vs correct answers
        correct_count = 0
        for i, user_answer in enumerate(submission.user_answers):
            if i < len(submission.questions):
                question = submission.questions[i]
                # Handle both string and integer correct answers
                correct_answer = question.get("answer", "")
                correct_answer_index = question.get("correct_answer", -1)
                
                # If correct_answer is an integer (index), get the actual option text
                if isinstance(correct_answer_index, int) and correct_answer_index >= 0:
                    options = question.get("options", [])
                    if correct_answer_index < len(options):
                        correct_answer = options[correct_answer_index]
                
                if user_answer == correct_answer:
                    correct_count += 1
        
        # Use the provided score or calculate it
        score = submission.score if submission.score > 0 else (correct_count / submission.total_questions) * 100
        
        # Use time_taken or time_spent
        time_spent = submission.time_spent if submission.time_spent else submission.time_taken
        
        # Generate test name if not provided
        test_name = submission.test_name or f"{submission.topic} Assessment"
        
        # Store result in database (mock implementation)
        db = await get_db()
        result_data = {
            "user_id": current_user.id,
            "test_name": test_name,
            "topic": submission.topic,
            "difficulty": submission.difficulty,
            "score": score,
            "correct_answers": correct_count,
            "total_questions": submission.total_questions,
            "time_spent": time_spent,
            "submitted_at": datetime.utcnow(),
            "questions": submission.questions,
            "user_answers": submission.user_answers,
            "explanations": submission.explanations
        }
        
        # In a real implementation, you would save to database:
        # result_id = await db.results.insert_one(result_data)
        
        print(f"[SUCCESS] [RESULTS] Assessment submitted for user {current_user.id}: {score:.1f}% ({correct_count}/{submission.total_questions})")
        
        return SubmissionResponse(
            success=True,
            score=score,
            correct_answers=correct_count,
            total_questions=submission.total_questions,
            message=f"Assessment completed! Score: {score:.1f}%"
        )
        
    except Exception as e:
        print(f"[ERROR] [RESULTS] Failed to submit assessment: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit assessment: {str(e)}"
        )

@router.get("/{result_id}/detailed")
async def get_detailed_result(
    result_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """Get detailed result with question reviews"""
    try:
        db = await get_db()
        
        # For now, return mock data since we don't have a real database implementation
        # In a real implementation, you would fetch from the database
        mock_result = {
            "id": result_id,
            "user_id": current_user.id,
            "score": 3,
            "total_questions": 3,
            "questions": [
                {
                    "question": "What is 2 + 2?",
                    "options": ["3", "4", "5", "6"],
                    "answer": "4",
                    "correct_answer": 1,
                    "explanation": "2 + 2 equals 4."
                },
                {
                    "question": "Which shape has 3 sides?",
                    "options": ["Square", "Circle", "Triangle", "Rectangle"],
                    "answer": "Triangle",
                    "correct_answer": 2,
                    "explanation": "A triangle has 3 sides."
                },
                {
                    "question": "What is the color of the sky on a clear day?",
                    "options": ["Green", "Red", "Blue", "Yellow"],
                    "answer": "Blue",
                    "correct_answer": 2,
                    "explanation": "The sky appears blue due to the scattering of sunlight."
                }
            ],
            "user_answers": ["4", "Triangle", "Blue"],
            "topic": "Science",
            "difficulty": "Easy",
            "time_taken": 120,
            "date": datetime.utcnow().isoformat(),
            "percentage": 100,
            "correct_answers": 3,
            "incorrect_answers": 0
        }
        
        # Generate question reviews with proper is_correct calculation
        question_reviews = []
        for i, question in enumerate(mock_result["questions"]):
            user_answer = mock_result["user_answers"][i] if i < len(mock_result["user_answers"]) else ""
            
            # Handle both string and integer correct answers
            correct_answer = question.get("answer", "")
            correct_answer_index = question.get("correct_answer", -1)
            
            if isinstance(correct_answer_index, int) and correct_answer_index >= 0:
                options = question.get("options", [])
                if correct_answer_index < len(options):
                    correct_answer = options[correct_answer_index]
            
            is_correct = user_answer == correct_answer
            
            question_reviews.append({
                "question_index": i,
                "question": question["question"],
                "options": question["options"],
                "correct_answer": correct_answer,
                "user_answer": user_answer,
                "is_correct": is_correct,
                "explanation": question.get("explanation", "")
            })
        
        return {
            "success": True,
            "result": mock_result,
            "question_reviews": question_reviews
        }
        
    except Exception as e:
        print(f"[ERROR] [RESULTS] Failed to get detailed result: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get detailed result: {str(e)}"
        )

@router.get("/health")
async def results_health_check():
    """Health check endpoint for results router"""
    return {
        "status": "healthy",
        "message": "Results router is working",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.post("/test")
async def test_results_endpoint():
    """Test endpoint for results router"""
    return {
        "status": "success",
        "message": "Results endpoint is accessible",
        "timestamp": datetime.utcnow().isoformat()
    }