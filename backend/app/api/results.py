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
from bson import ObjectId

router = APIRouter()

async def update_user_progress(db, user_id: str, score: int, percentage: float, total_questions: int):
    """Update user's gamification progress after completing an assessment"""
    try:
        # Get current user data
        user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user_doc:
            return
        
        # Calculate XP based on score and questions
        base_xp = 10  # Base XP for completing assessment
        score_xp = int(percentage * 0.5)  # XP based on percentage (0-50 XP)
        question_xp = total_questions * 2  # 2 XP per question
        total_xp = base_xp + score_xp + question_xp
        
        # Calculate new level (every 100 XP = 1 level)
        current_xp = user_doc.get("xp", 0)
        new_xp = current_xp + total_xp
        new_level = (new_xp // 100) + 1
        
        # Update streak (simplified - just increment if assessment completed)
        current_streak = user_doc.get("streak", 0)
        new_streak = current_streak + 1
        
        # Update longest streak
        current_longest_streak = user_doc.get("longest_streak", 0)
        new_longest_streak = max(current_longest_streak, new_streak)
        
        # Check for badges
        badges = user_doc.get("badges", [])
        new_badges = []
        
        # First assessment badge
        if "first_assessment" not in badges:
            new_badges.append("first_assessment")
        
        # High score badge (90%+)
        if percentage >= 90 and "high_scorer" not in badges:
            new_badges.append("high_scorer")
        
        # Streak badges
        if new_streak >= 5 and "consistent_learner" not in badges:
            new_badges.append("consistent_learner")
        
        # Level up badge
        old_level = (current_xp // 100) + 1
        if new_level > old_level and "level_up" not in badges:
            new_badges.append("level_up")
        
        # Update user document
        update_data = {
            "xp": new_xp,
            "level": new_level,
            "streak": new_streak,
            "longest_streak": new_longest_streak,
            "last_activity": datetime.utcnow(),
            "completed_assessments": user_doc.get("completed_assessments", 0) + 1,
            "total_questions_answered": user_doc.get("total_questions_answered", 0) + total_questions,
            "average_score": calculate_average_score(user_doc, percentage)
        }
        
        # Add new badges
        if new_badges:
            update_data["badges"] = badges + new_badges
        
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        
        print(f"[SUCCESS] [GAMIFICATION] Updated user {user_id}: +{total_xp} XP, Level {new_level}, Streak {new_streak}")
        if new_badges:
            print(f"[SUCCESS] [GAMIFICATION] New badges earned: {new_badges}")
            
    except Exception as e:
        print(f"[ERROR] [GAMIFICATION] Failed to update user progress: {str(e)}")

def calculate_average_score(user_doc: dict, new_percentage: float) -> float:
    """Calculate new average score"""
    current_avg = user_doc.get("average_score", 0)
    completed_count = user_doc.get("completed_assessments", 0)
    
    if completed_count == 0:
        return new_percentage
    else:
        # Weighted average
        return ((current_avg * completed_count) + new_percentage) / (completed_count + 1)

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
        if str(current_user.id) != user_id and current_user.role not in ["admin", "teacher"]:
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
        if str(current_user.id) != user_id and current_user.role not in ["admin", "teacher"]:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to access this user's analytics"
            )
        
        # Get real analytics data from database
        db = await get_db()
        user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
        
        if not user_doc:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        
        # Get user's assessment results
        results_cursor = db.results.find({"user_id": user_id}).sort("submitted_at", -1).limit(10)
        results = await results_cursor.to_list(length=10)
        
        # Calculate analytics from real data
        total_tests = user_doc.get("completed_assessments", 0)
        average_score = user_doc.get("average_score", 0)
        total_questions = user_doc.get("total_questions_answered", 0)
        streak_days = user_doc.get("streak", 0)
        
        # Get recent performance data
        recent_performance = []
        for result in results:
            if result.get("submitted_at"):
                recent_performance.append({
                    "date": result["submitted_at"].strftime("%Y-%m-%d") if hasattr(result["submitted_at"], 'strftime') else str(result["submitted_at"]),
                    "score": result.get("score", 0)
                })
        
        analytics_data = {
            "success": True,
            "analytics": {
                "total_assessments": total_tests,
                "total_questions": total_questions,
                "average_score": average_score,
                "streak_days": streak_days,
                "topics": ["Mathematics", "Science", "Programming"],  # Default topics
                "recent_performance": recent_performance
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
        
        # Save to database
        result_id = await db.results.insert_one(result_data)
        
        # Update user gamification data
        await update_user_progress(db, str(current_user.id), correct_count, score, submission.total_questions)
        
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
            "user_id": str(current_user.id),
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