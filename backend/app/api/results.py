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
    topic: Optional[str] = ""
    difficulty: Optional[str] = "medium"
    percentage: Optional[float] = None
    time_taken: Optional[int] = None
    date: Optional[datetime] = None

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
        
        # Get real results from database
        # Check multiple collections for results
        results = []
        
        # Get from db.results collection (general test results)
        results_cursor = db.results.find({"user_id": ObjectId(user_id)}).sort("submitted_at", -1)
        db_results = await results_cursor.to_list(length=None)
        
        for result in db_results:
            score = result.get("score", 0)
            total_questions = result.get("total_questions", 0)
            percentage = (score / total_questions * 100) if total_questions > 0 else 0
            
            results.append(TestResult(
                id=str(result["_id"]),
                test_name=result.get("test_name", "Unknown Test"),
                score=score,
                total_questions=total_questions,
                correct_answers=result.get("correct_answers", 0),
                completed_at=result.get("submitted_at", datetime.utcnow()),
                duration=result.get("time_spent", 0),
                topic=result.get("topic", ""),
                difficulty=result.get("difficulty", "medium"),
                percentage=percentage,
                time_taken=result.get("time_spent", 0),
                date=result.get("submitted_at", datetime.utcnow())
            ))
        
        # Get from db.assessment_results collection (assessment submissions)
        assessment_results_cursor = db.assessment_results.find({"student_id": user_id}).sort("submitted_at", -1)
        assessment_results = await assessment_results_cursor.to_list(length=None)
        
        for result in assessment_results:
            score = result.get("score", 0)
            total_questions = result.get("total_questions", 0)
            percentage = (score / total_questions * 100) if total_questions > 0 else 0
            
            results.append(TestResult(
                id=str(result["_id"]),
                test_name=result.get("assessment_title", "Assessment"),
                score=score,
                total_questions=total_questions,
                correct_answers=result.get("score", 0),  # For assessment results, score is the correct count
                completed_at=result.get("submitted_at", datetime.utcnow()),
                duration=result.get("time_taken", 0),
                topic=result.get("subject", ""),
                difficulty=result.get("difficulty", "medium"),
                percentage=percentage,
                time_taken=result.get("time_taken", 0),
                date=result.get("submitted_at", datetime.utcnow())
            ))
        
        # Get from db.assessment_submissions collection (assessment submissions)
        submission_results_cursor = db.assessment_submissions.find({"student_id": user_id}).sort("submitted_at", -1)
        submission_results = await submission_results_cursor.to_list(length=None)
        
        for result in submission_results:
            # Get assessment details
            assessment = await db.assessments.find_one({"_id": ObjectId(result["assessment_id"])})
            assessment_title = assessment.get("title", "Assessment") if assessment else "Assessment"
            
            score = result.get("score", 0)
            total_questions = result.get("total_questions", 0)
            percentage = (score / total_questions * 100) if total_questions > 0 else 0
            
            results.append(TestResult(
                id=str(result["_id"]),
                test_name=assessment_title,
                score=score,
                total_questions=total_questions,
                correct_answers=result.get("score", 0),
                completed_at=result.get("submitted_at", datetime.utcnow()),
                duration=result.get("time_taken", 0),
                topic=assessment.get("subject", "") if assessment else "",
                difficulty=assessment.get("difficulty", "medium") if assessment else "medium",
                percentage=percentage,
                time_taken=result.get("time_taken", 0),
                date=result.get("submitted_at", datetime.utcnow())
            ))
        
        # Sort all results by completion date (most recent first)
        results.sort(key=lambda x: x.completed_at, reverse=True)
        
        return UserResultsResponse(
            success=True,
            results=results,
            total=len(results)
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
        
        # Get real result from database
        result = await db.results.find_one({"_id": ObjectId(result_id)})
        if not result:
            raise HTTPException(status_code=404, detail="Result not found")
        
        # Verify user can access this result
        result_user_id = result.get("user_id")
        if isinstance(result_user_id, ObjectId):
            result_user_id = str(result_user_id)
        
        if result_user_id != str(current_user.id) and current_user.role not in ["admin", "teacher"]:
            raise HTTPException(status_code=403, detail="Not authorized to access this result")
        
        # Extract real data from the result
        real_result = {
            "id": str(result["_id"]),
            "user_id": str(result.get("user_id")),
            "score": result.get("score", 0),
            "total_questions": result.get("total_questions", 0),
            "questions": result.get("questions", []),
            "user_answers": result.get("user_answers", []),
            "topic": result.get("topic", ""),
            "difficulty": result.get("difficulty", "medium"),
            "time_taken": result.get("time_spent", 0),
            "date": result.get("submitted_at", datetime.utcnow()).isoformat(),
            "percentage": (result.get("score", 0) / result.get("total_questions", 1)) * 100,
            "correct_answers": result.get("correct_answers", 0),
            "incorrect_answers": result.get("total_questions", 0) - result.get("correct_answers", 0)
        }
        
        # Generate question reviews with proper is_correct calculation
        question_reviews = []
        for i, question in enumerate(real_result["questions"]):
            user_answer = real_result["user_answers"][i] if i < len(real_result["user_answers"]) else ""
            
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
            "result": real_result,
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