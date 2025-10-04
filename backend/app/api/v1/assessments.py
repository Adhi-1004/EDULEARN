"""
Assessment endpoints
Handles assessment creation, management, and evaluation
"""
from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

from ...core.security import security_manager
from ...db import get_db
from ...models.models import UserModel
from ...dependencies import require_teacher_or_admin, require_assessment_creation

router = APIRouter()

# Request/Response Models
class AssessmentCreate(BaseModel):
    title: str
    description: str
    subject: str
    difficulty: str = Field(..., regex="^(easy|medium|hard)$")
    time_limit: int = Field(..., ge=1, le=300)  # minutes
    questions: List[Dict[str, Any]]

class AssessmentResponse(BaseModel):
    assessment_id: str
    title: str
    description: str
    subject: str
    difficulty: str
    time_limit: int
    created_by: str
    created_at: datetime
    is_active: bool
    total_questions: int

class AssessmentSubmission(BaseModel):
    assessment_id: str
    answers: List[Dict[str, Any]]
    time_taken: int  # seconds

class AssessmentResult(BaseModel):
    submission_id: str
    assessment_id: str
    student_id: str
    score: float
    total_questions: int
    correct_answers: int
    time_taken: int
    submitted_at: datetime

@router.post("/", response_model=AssessmentResponse)
async def create_assessment(
    assessment: AssessmentCreate,
    current_user: UserModel = Depends(require_assessment_creation)
):
    """Create a new assessment"""
    try:
        db = await get_db()
        
        # Create assessment document
        assessment_doc = {
            "title": assessment.title,
            "description": assessment.description,
            "subject": assessment.subject,
            "difficulty": assessment.difficulty,
            "time_limit": assessment.time_limit,
            "questions": assessment.questions,
            "created_by": str(current_user.id),
            "created_at": datetime.utcnow(),
            "is_active": True,
            "total_questions": len(assessment.questions)
        }
        
        # Insert assessment
        result = await db.assessments.insert_one(assessment_doc)
        assessment_doc["_id"] = result.inserted_id
        
        return AssessmentResponse(
            assessment_id=str(assessment_doc["_id"]),
            title=assessment_doc["title"],
            description=assessment_doc["description"],
            subject=assessment_doc["subject"],
            difficulty=assessment_doc["difficulty"],
            time_limit=assessment_doc["time_limit"],
            created_by=assessment_doc["created_by"],
            created_at=assessment_doc["created_at"],
            is_active=assessment_doc["is_active"],
            total_questions=assessment_doc["total_questions"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create assessment: {str(e)}"
        )

@router.get("/", response_model=List[AssessmentResponse])
async def get_assessments(
    subject: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    is_active: bool = Query(True),
    current_user: UserModel = Depends(require_teacher_or_admin)
):
    """Get list of assessments"""
    try:
        db = await get_db()
        
        # Build filter
        filter_dict = {"is_active": is_active}
        if subject:
            filter_dict["subject"] = subject
        if difficulty:
            filter_dict["difficulty"] = difficulty
        
        # Get assessments
        assessments_cursor = db.assessments.find(filter_dict).sort("created_at", -1)
        assessments = []
        
        async for assessment_doc in assessments_cursor:
            assessments.append(AssessmentResponse(
                assessment_id=str(assessment_doc["_id"]),
                title=assessment_doc["title"],
                description=assessment_doc["description"],
                subject=assessment_doc["subject"],
                difficulty=assessment_doc["difficulty"],
                time_limit=assessment_doc["time_limit"],
                created_by=assessment_doc["created_by"],
                created_at=assessment_doc["created_at"],
                is_active=assessment_doc["is_active"],
                total_questions=assessment_doc["total_questions"]
            ))
        
        return assessments
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get assessments: {str(e)}"
        )

@router.get("/{assessment_id}", response_model=AssessmentResponse)
async def get_assessment(
    assessment_id: str,
    current_user: UserModel = Depends(require_teacher_or_admin)
):
    """Get specific assessment by ID"""
    try:
        db = await get_db()
        
        assessment_doc = await db.assessments.find_one({"_id": assessment_id})
        if not assessment_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment not found"
            )
        
        return AssessmentResponse(
            assessment_id=str(assessment_doc["_id"]),
            title=assessment_doc["title"],
            description=assessment_doc["description"],
            subject=assessment_doc["subject"],
            difficulty=assessment_doc["difficulty"],
            time_limit=assessment_doc["time_limit"],
            created_by=assessment_doc["created_by"],
            created_at=assessment_doc["created_at"],
            is_active=assessment_doc["is_active"],
            total_questions=assessment_doc["total_questions"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get assessment: {str(e)}"
        )

@router.post("/{assessment_id}/submit", response_model=AssessmentResult)
async def submit_assessment(
    assessment_id: str,
    submission: AssessmentSubmission,
    current_user: UserModel = Depends(require_teacher_or_admin)
):
    """Submit assessment answers"""
    try:
        db = await get_db()
        
        # Get assessment
        assessment_doc = await db.assessments.find_one({"_id": assessment_id})
        if not assessment_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment not found"
            )
        
        # Calculate score (placeholder logic)
        total_questions = len(assessment_doc["questions"])
        correct_answers = 0
        
        for i, question in enumerate(assessment_doc["questions"]):
            if i < len(submission.answers):
                # Simple scoring logic (should be more sophisticated)
                if submission.answers[i].get("answer") == question.get("correct_answer"):
                    correct_answers += 1
        
        score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        
        # Create submission record
        submission_doc = {
            "assessment_id": assessment_id,
            "student_id": str(current_user.id),
            "answers": submission.answers,
            "score": score,
            "total_questions": total_questions,
            "correct_answers": correct_answers,
            "time_taken": submission.time_taken,
            "submitted_at": datetime.utcnow()
        }
        
        # Insert submission
        result = await db.assessment_submissions.insert_one(submission_doc)
        submission_doc["_id"] = result.inserted_id
        
        return AssessmentResult(
            submission_id=str(submission_doc["_id"]),
            assessment_id=submission_doc["assessment_id"],
            student_id=submission_doc["student_id"],
            score=submission_doc["score"],
            total_questions=submission_doc["total_questions"],
            correct_answers=submission_doc["correct_answers"],
            time_taken=submission_doc["time_taken"],
            submitted_at=submission_doc["submitted_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit assessment: {str(e)}"
        )

@router.get("/{assessment_id}/results", response_model=List[AssessmentResult])
async def get_assessment_results(
    assessment_id: str,
    current_user: UserModel = Depends(require_teacher_or_admin)
):
    """Get results for a specific assessment"""
    try:
        db = await get_db()
        
        # Get all submissions for this assessment
        submissions_cursor = db.assessment_submissions.find({"assessment_id": assessment_id})
        results = []
        
        async for submission_doc in submissions_cursor:
            results.append(AssessmentResult(
                submission_id=str(submission_doc["_id"]),
                assessment_id=submission_doc["assessment_id"],
                student_id=submission_doc["student_id"],
                score=submission_doc["score"],
                total_questions=submission_doc["total_questions"],
                correct_answers=submission_doc["correct_answers"],
                time_taken=submission_doc["time_taken"],
                submitted_at=submission_doc["submitted_at"]
            ))
        
        return results
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get assessment results: {str(e)}"
        )
