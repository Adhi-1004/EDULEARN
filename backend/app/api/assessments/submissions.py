"""
Assessment Submission Handling
Handles student submissions, scoring, and result processing
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from ...db import get_db
from ...schemas.schemas import (
    AssessmentSubmission, AssessmentResult, AssessmentSubmissionResponse,
    CodingSubmission, CodingSubmissionResponse, AssessmentLeaderboard, LeaderboardEntry
)
from ...dependencies import get_current_user
from ...models.models import UserModel
from .notifications import create_assessment_completion_notification

router = APIRouter(prefix="/assessments", tags=["assessments-submissions"])

@router.get("/student/available", response_model=List[AssessmentSubmissionResponse])
async def get_available_assessments(user: UserModel = Depends(get_current_user)):
    """Get assessments available to the current student"""
    try:
        db = await get_db()
        
        if user.role != "student":
            raise HTTPException(status_code=403, detail="Only students can access this endpoint")
        
        # Get student's batch
        student = await db.users.find_one({"_id": ObjectId(user.id)})
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        student_batch_id = student.get("batch_id")
        if not student_batch_id:
            return []  # No batch assigned
        
        # Get assessments assigned to student's batch
        assessments = await db.assessments.find({
            "assigned_batches": str(student_batch_id),
            "status": {"$in": ["published", "active"]},
            "is_active": True
        }).to_list(length=None)
        
        # Also check teacher assessments
        teacher_assessments = await db.teacher_assessments.find({
            "batches": str(student_batch_id),
            "status": {"$in": ["published", "active"]},
            "is_active": True
        }).to_list(length=None)
        
        # Format assessments
        available_assessments = []
        
        for assessment in assessments:
            # Check if student already submitted
            existing_submission = await db.assessment_submissions.find_one({
                "assessment_id": str(assessment["_id"]),
                "student_id": user.id
            })
            
            if existing_submission:
                continue  # Skip if already submitted
            
            available_assessments.append(AssessmentSubmissionResponse(
                id=str(assessment["_id"]),
                assessment_id=str(assessment["_id"]),
                student_id=user.id,
                student_name=user.username or user.email,
                student_email=user.email,
                score=0,  # Not submitted yet
                percentage=0.0,
                time_taken=0,
                submitted_at=datetime.utcnow().isoformat(),
                total_questions=assessment["question_count"]
            ))
        
        for assessment in teacher_assessments:
            # Check if student already submitted
            existing_submission = await db.teacher_assessment_results.find_one({
                "assessment_id": str(assessment["_id"]),
                "student_id": user.id
            })
            
            if existing_submission:
                continue  # Skip if already submitted
            
            available_assessments.append(AssessmentSubmissionResponse(
                id=str(assessment["_id"]),
                assessment_id=str(assessment["_id"]),
                student_id=user.id,
                student_name=user.username or user.email,
                student_email=user.email,
                score=0,  # Not submitted yet
                percentage=0.0,
                time_taken=0,
                submitted_at=datetime.utcnow().isoformat(),
                total_questions=assessment["question_count"]
            ))
        
        return available_assessments
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/student/upcoming")
async def get_student_upcoming_assessments(user: UserModel = Depends(get_current_user)):
    """Get upcoming assessments for the current student"""
    try:
        db = await get_db()
        
        if user.role != "student":
            raise HTTPException(status_code=403, detail="Only students can access this endpoint")
        
        # For now, return empty array as student-generated assessments are handled differently
        # This endpoint is mainly for teacher-assigned assessments that are scheduled
        return []
    
    except Exception as e:
        print(f"[ERROR] [ASSESSMENTS] Error fetching upcoming student assessments: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch upcoming assessments: {str(e)}")

@router.get("/teacher/upcoming")
async def get_teacher_upcoming_assessments(user: UserModel = Depends(get_current_user)):
    """Get upcoming assessments for the current teacher"""
    try:
        db = await get_db()
        
        if user.role != "teacher":
            raise HTTPException(status_code=403, detail="Only teachers can access this endpoint")
        
        # Get teacher's upcoming assessments
        assessments = await db.assessments.find({
            "created_by": ObjectId(user.id),
            "status": {"$in": ["draft", "scheduled"]},
            "is_active": True
        }).to_list(length=None)
        
        # Format the response
        upcoming_assessments = []
        for assessment in assessments:
            upcoming_assessments.append({
                "id": str(assessment["_id"]),
                "title": assessment.get("title", "Untitled Assessment"),
                "description": assessment.get("description", ""),
                "status": assessment.get("status", "draft"),
                "created_at": assessment.get("created_at", datetime.utcnow()),
                "scheduled_date": assessment.get("scheduled_date"),
                "due_date": assessment.get("due_date"),
                "question_count": len(assessment.get("questions", [])),
                "assigned_batches": assessment.get("assigned_batches", [])
            })
        
        return upcoming_assessments
    
    except Exception as e:
        print(f"[ERROR] [ASSESSMENTS] Error fetching upcoming teacher assessments: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch upcoming assessments: {str(e)}")

@router.post("/{assessment_id}/submit", response_model=AssessmentResult)
async def submit_assessment(
    assessment_id: str,
    submission_data: AssessmentSubmission,
    user: UserModel = Depends(get_current_user)
):
    """Submit assessment answers"""
    try:
        db = await get_db()
        
        if user.role != "student":
            raise HTTPException(status_code=403, detail="Only students can submit assessments")
        
        if not ObjectId.is_valid(assessment_id):
            raise HTTPException(status_code=400, detail="Invalid assessment ID")
        
        # Get assessment
        assessment = await db.assessments.find_one({"_id": ObjectId(assessment_id)})
        
        if not assessment:
            # Try teacher assessments
            assessment = await db.teacher_assessments.find_one({"_id": ObjectId(assessment_id)})
        
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        # Check if assessment is available
        if assessment.get("status") not in ["published", "active"]:
            raise HTTPException(status_code=403, detail="Assessment not available")
        
        # Check if student already submitted
        existing_submission = await db.assessment_submissions.find_one({
            "assessment_id": assessment_id,
            "student_id": user.id
        })
        
        if existing_submission:
            raise HTTPException(status_code=400, detail="Assessment already submitted")
        
        # Get questions
        questions = assessment.get("questions", [])
        if not questions:
            raise HTTPException(status_code=400, detail="Assessment has no questions")
        
        # Calculate score
        correct_answers = 0
        total_questions = len(questions)
        
        for i, question in enumerate(questions):
            if i < len(submission_data.answers):
                if submission_data.answers[i] == question.get("correct_answer", -1):
                    correct_answers += 1
        
        score = correct_answers
        percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        
        # Create submission record
        submission_doc = {
            "assessment_id": assessment_id,
            "student_id": user.id,
            "student_name": user.username or user.email,
            "student_email": user.email,
            "answers": submission_data.answers,
            "score": score,
            "percentage": percentage,
            "time_taken": submission_data.time_taken,
            "submitted_at": datetime.utcnow(),
            "total_questions": total_questions,
            "attempt_number": 1
        }
        
        result = await db.assessment_submissions.insert_one(submission_doc)
        
        # Update user progress (gamification)
        await update_user_progress(db, user.id, score, percentage, total_questions)
        
        # Create completion notification
        teacher_id = assessment.get("created_by") or assessment.get("teacher_id")
        await create_assessment_completion_notification(
            db, user.id, assessment["title"], percentage, teacher_id
        )
        
        return AssessmentResult(
            id=str(result.inserted_id),
            assessment_id=assessment_id,
            student_id=user.id,
            student_name=user.username or user.email,
            score=float(score),
            total_questions=total_questions,
            percentage=percentage,
            time_taken=submission_data.time_taken,
            submitted_at=datetime.utcnow().isoformat(),
            attempt_number=1
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{assessment_id}/coding-submit", response_model=CodingSubmissionResponse)
async def submit_coding_solution(
    assessment_id: str,
    submission_data: CodingSubmission,
    user: UserModel = Depends(get_current_user)
):
    """Submit coding solution"""
    try:
        db = await get_db()
        
        if user.role != "student":
            raise HTTPException(status_code=403, detail="Only students can submit coding solutions")
        
        if not ObjectId.is_valid(assessment_id):
            raise HTTPException(status_code=400, detail="Invalid assessment ID")
        
        # Get assessment and question
        assessment = await db.assessments.find_one({"_id": ObjectId(assessment_id)})
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        # Find the coding question
        question = None
        for q in assessment.get("questions", []):
            if q.get("id") == submission_data.question_id:
                question = q
                break
        
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        # Execute code (simplified - in production, use proper code execution service)
        execution_result = await execute_code(submission_data.code, submission_data.language, question.get("test_cases", []))
        
        # Create submission record
        submission_doc = {
            "assessment_id": assessment_id,
            "question_id": submission_data.question_id,
            "student_id": user.id,
            "code": submission_data.code,
            "language": submission_data.language,
            "status": execution_result["status"],
            "execution_time": execution_result["execution_time"],
            "memory_used": execution_result["memory_used"],
            "test_results": execution_result["test_results"],
            "score": execution_result["score"],
            "max_score": question.get("points", 10),
            "submitted_at": datetime.utcnow()
        }
        
        result = await db.coding_submissions.insert_one(submission_doc)
        
        return CodingSubmissionResponse(
            id=str(result.inserted_id),
            assessment_id=assessment_id,
            question_id=submission_data.question_id,
            status=execution_result["status"],
            execution_time=execution_result["execution_time"],
            memory_used=execution_result["memory_used"],
            test_results=execution_result["test_results"],
            score=execution_result["score"],
            max_score=question.get("points", 10),
            submitted_at=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{assessment_id}/leaderboard", response_model=AssessmentLeaderboard)
async def get_assessment_leaderboard(assessment_id: str, user: UserModel = Depends(get_current_user)):
    """Get leaderboard for an assessment"""
    try:
        db = await get_db()
        
        if not ObjectId.is_valid(assessment_id):
            raise HTTPException(status_code=400, detail="Invalid assessment ID")
        
        # Get submissions
        submissions = await db.assessment_submissions.find({
            "assessment_id": assessment_id
        }).sort("percentage", -1).to_list(length=None)
        
        # Format leaderboard
        leaderboard = []
        for i, submission in enumerate(submissions):
            leaderboard.append(LeaderboardEntry(
                student_id=submission["student_id"],
                student_name=submission["student_name"],
                score=submission["score"],
                percentage=submission["percentage"],
                time_taken=submission.get("time_taken"),
                rank=i + 1
            ))
        
        # Get assessment title
        assessment = await db.assessments.find_one({"_id": ObjectId(assessment_id)})
        if not assessment:
            assessment = await db.teacher_assessments.find_one({"_id": ObjectId(assessment_id)})
        
        title = assessment["title"] if assessment else "Unknown Assessment"
        
        return AssessmentLeaderboard(
            assessment_id=assessment_id,
            assessment_title=title,
            total_students=len(submissions),
            leaderboard=leaderboard
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
        
        # Update streak
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
    
    total_score = current_avg * completed_count
    new_total_score = total_score + new_percentage
    new_avg = new_total_score / (completed_count + 1)
    
    return round(new_avg, 2)

async def execute_code(code: str, language: str, test_cases: List[Dict]) -> Dict:
    """Execute code and return results (simplified implementation)"""
    # This is a placeholder - in production, use proper code execution service
    return {
        "status": "success",
        "execution_time": 100,
        "memory_used": 64,
        "test_results": [{"passed": True, "input": "test", "expected": "output", "actual": "output"}],
        "score": 10
    }
