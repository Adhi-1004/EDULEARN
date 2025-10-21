"""
Core Assessment CRUD Operations
Handles basic assessment creation, retrieval, and management
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from ...db import get_db
from ...schemas.schemas import (
    AssessmentCreate, AssessmentResponse, QuestionCreate, QuestionResponse,
    CodingQuestionCreate, CodingQuestionResponse
)
from ...dependencies import require_teacher, get_current_user
from ...models.models import UserModel
from .notifications import send_assessment_notifications

router = APIRouter(prefix="/assessments", tags=["assessments-core"])

@router.post("/", response_model=AssessmentResponse)
async def create_assessment(assessment_data: AssessmentCreate, user: UserModel = Depends(require_teacher)):
    """Create a new assessment - Teacher/Admin only"""
    try:
        db = await get_db()
        
        assessment_doc = {
            "title": assessment_data.title,
            "subject": assessment_data.subject,
            "difficulty": assessment_data.difficulty,
            "description": assessment_data.description,
            "time_limit": assessment_data.time_limit,
            "max_attempts": assessment_data.max_attempts,
            "type": assessment_data.type,
            "created_by": str(user.id),
            "created_at": datetime.utcnow(),
            "status": "draft",
            "question_count": len(assessment_data.questions),
            "questions": assessment_data.questions,
            "assigned_batches": assessment_data.batches,
            "is_active": False
        }
        
        result = await db.assessments.insert_one(assessment_doc)
        assessment_id = str(result.inserted_id)
        
        # Generate questions if assessment type is AI-generated
        if assessment_data.type == "ai" and len(assessment_data.questions) == 0:
            try:
                from app.services.gemini_coding_service import GeminiCodingService
                gemini_service = GeminiCodingService()
                
                # Generate questions based on topic and difficulty
                generated_questions = await gemini_service.generate_mcq_questions(
                    topic=assessment_data.subject,
                    difficulty=assessment_data.difficulty,
                    count=10  # Default count, can be made configurable
                )
                
                # Update assessment with generated questions
                await db.assessments.update_one(
                    {"_id": result.inserted_id},
                    {"$set": {
                        "questions": generated_questions,
                        "question_count": len(generated_questions),
                        "is_active": True,
                        "status": "active"
                    }}
                )
                
                # Send notifications to students in selected batches
                await send_assessment_notifications(db, assessment_id, assessment_data.batches, assessment_data.title)
                
            except Exception as e:
                print(f"❌ [ASSESSMENT] Error generating questions: {str(e)}")
                # Continue with empty questions if generation fails
        
        return AssessmentResponse(
            id=assessment_id,
            title=assessment_data.title,
            subject=assessment_data.subject,
            difficulty=assessment_data.difficulty,
            description=assessment_data.description,
            time_limit=assessment_data.time_limit,
            max_attempts=assessment_data.max_attempts,
            question_count=len(assessment_data.questions),
            created_by=str(user.id),
            created_at=assessment_doc["created_at"].isoformat(),
            status="active" if assessment_data.type == "ai" else "draft",
            type=assessment_doc["type"],
            is_active=True if assessment_data.type == "ai" else False,
            total_questions=len(assessment_data.questions)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[AssessmentResponse])
async def get_teacher_assessments(user: UserModel = Depends(get_current_user)):
    """Get all assessments created by the current teacher across sources (manual and teacher-created)."""
    try:
        db = await get_db()
        
        # Get manual assessments
        manual_list = await db.assessments.find({"created_by": str(user.id)}).to_list(length=None)
        
        # Teacher-created (AI/generated) assessments
        teacher_list = await db.teacher_assessments.find({"teacher_id": str(user.id)}).to_list(length=None)
        
        # Combine and format both lists
        all_assessments = []
        
        # Process manual assessments
        for assessment in manual_list:
            all_assessments.append(AssessmentResponse(
                id=str(assessment["_id"]),
                title=assessment["title"],
                subject=assessment["subject"],
                difficulty=assessment["difficulty"],
                description=assessment["description"],
                time_limit=assessment["time_limit"],
                max_attempts=assessment["max_attempts"],
                question_count=assessment["question_count"],
                created_by=assessment["created_by"],
                created_at=assessment["created_at"].isoformat(),
                status=assessment["status"],
                type=assessment["type"],
                is_active=assessment["is_active"],
                total_questions=assessment["question_count"],
                assigned_batches=assessment.get("assigned_batches", [])
            ))
        
        # Process teacher-created assessments
        for assessment in teacher_list:
            all_assessments.append(AssessmentResponse(
                id=str(assessment["_id"]),
                title=assessment["title"],
                subject=assessment.get("topic", assessment.get("subject", "General")),
                difficulty=assessment["difficulty"],
                description=f"Teacher-created assessment on {assessment.get('topic', assessment.get('subject', 'General'))}",
                time_limit=30,  # Default time limit
                max_attempts=1,  # Default max attempts
                question_count=assessment["question_count"],
                created_by=str(assessment["teacher_id"]),
                created_at=assessment["created_at"].isoformat(),
                status=assessment["status"],
                type=assessment["type"],
                is_active=assessment["is_active"],
                total_questions=assessment["question_count"],
                assigned_batches=assessment.get("batches", [])
            ))
        
        # Sort by creation date (newest first)
        all_assessments.sort(key=lambda x: x.created_at, reverse=True)
        
        return all_assessments
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{assessment_id}/details")
async def get_assessment_details(assessment_id: str, user: UserModel = Depends(get_current_user)):
    """Get detailed information about a specific assessment"""
    try:
        db = await get_db()
        
        if not ObjectId.is_valid(assessment_id):
            raise HTTPException(status_code=400, detail="Invalid assessment ID")
        
        # Try to find in regular assessments first
        assessment = await db.assessments.find_one({"_id": ObjectId(assessment_id)})
        
        if not assessment:
            # Try teacher assessments
            assessment = await db.teacher_assessments.find_one({"_id": ObjectId(assessment_id)})
        
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        # Check permissions
        if user.role == "student":
            # Students can only see published assessments assigned to them
            if assessment.get("status") != "published" and assessment.get("status") != "active":
                raise HTTPException(status_code=403, detail="Assessment not available")
        elif user.role == "teacher":
            # Teachers can only see their own assessments
            if assessment.get("created_by") != str(user.id) and assessment.get("teacher_id") != str(user.id):
                raise HTTPException(status_code=403, detail="Access denied")
        
        # Format response based on assessment type
        if "teacher_id" in assessment:
            # Teacher-created assessment
            return {
                "id": str(assessment["_id"]),
                "title": assessment["title"],
                "topic": assessment.get("topic", assessment.get("subject", "General")),
                "difficulty": assessment["difficulty"],
                "question_count": assessment["question_count"],
                "questions": assessment.get("questions", []),
                "batches": assessment.get("batches", []),
                "teacher_id": str(assessment["teacher_id"]),
                "type": assessment["type"],
                "status": assessment["status"],
                "is_active": assessment["is_active"],
                "created_at": assessment["created_at"].isoformat(),
                "created_by": str(assessment.get("teacher_id", assessment.get("created_by", "unknown"))),
                "created_at": assessment.get("created_at", datetime.utcnow()).isoformat(),
            }
        else:
            # Regular assessment
            return {
                "id": str(assessment["_id"]),
                "title": assessment["title"],
                "subject": assessment["subject"],
                "difficulty": assessment["difficulty"],
                "description": assessment["description"],
                "time_limit": assessment["time_limit"],
                "max_attempts": assessment["max_attempts"],
                "question_count": assessment["question_count"],
                "questions": assessment.get("questions", []),
                "assigned_batches": assessment.get("assigned_batches", []),
                "created_by": assessment["created_by"],
                "created_at": assessment["created_at"].isoformat(),
                "status": assessment["status"],
                "type": assessment["type"],
                "is_active": assessment["is_active"],
                "total_questions": assessment["question_count"]
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{assessment_id}/publish")
async def publish_assessment(assessment_id: str, user: UserModel = Depends(get_current_user)):
    """Publish an assessment to make it available to students"""
    try:
        db = await get_db()
        
        if user.role != "teacher":
            raise HTTPException(status_code=403, detail="Only teachers can publish assessments")
        
        if not ObjectId.is_valid(assessment_id):
            raise HTTPException(status_code=400, detail="Invalid assessment ID")
        
        # Update assessment status
        result = await db.assessments.update_one(
            {"_id": ObjectId(assessment_id), "created_by": str(user.id)},
            {"$set": {"status": "published", "is_active": True}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Assessment not found or access denied")
        
        # Get assessment details for notifications
        assessment = await db.assessments.find_one({"_id": ObjectId(assessment_id)})
        
        # Get assigned batches
        assigned_batches = assessment.get("assigned_batches", [])
        
        # Create notifications for students in assigned batches
        for batch_id in assigned_batches:
            # Get students in this batch
            batch = await db.batches.find_one({"_id": ObjectId(batch_id)})
            if batch:
                student_ids = batch.get("student_ids", [])
                
                # Create notifications for each student
                notifications = []
                for student_id in student_ids:
                    # Prefer subject if topic is not present
                    subject_or_topic = assessment.get("subject") or assessment.get("topic", "Assessment")
                    notification = {
                        "student_id": student_id,
                        "type": "assessment_assigned",
                        "title": f"New Assessment: {assessment.get('title', 'Untitled')}",
                        "message": f"A new {assessment.get('difficulty', 'medium')} assessment on {subject_or_topic} has been assigned to you.",
                        "assessment_id": assessment_id,
                        "created_at": datetime.utcnow(),
                        "is_read": False
                    }
                    notifications.append(notification)
                
                if notifications:
                    await db.notifications.insert_many(notifications)
        
        return {"success": True, "message": "Assessment published successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{assessment_id}/assign-batches")
async def assign_assessment_to_batches(
    assessment_id: str, 
    batch_ids: List[str], 
    user: UserModel = Depends(get_current_user)
):
    """Assign assessment to specific batches"""
    try:
        db = await get_db()
        
        if user.role != "teacher":
            raise HTTPException(status_code=403, detail="Only teachers can assign assessments")
        
        if not ObjectId.is_valid(assessment_id):
            raise HTTPException(status_code=400, detail="Invalid assessment ID")
        
        # Validate batch IDs
        valid_batch_ids = []
        for batch_id in batch_ids:
            if ObjectId.is_valid(batch_id):
                batch = await db.batches.find_one({
                    "_id": ObjectId(batch_id), 
                    "teacher_id": str(user.id)
                })
                if batch:
                    valid_batch_ids.append(batch_id)
        
        # Update assessment with assigned batches
        await db.assessments.update_one(
            {"_id": ObjectId(assessment_id)},
            {"$set": {"assigned_batches": valid_batch_ids}}
        )
        
        return {"success": True, "message": f"Assessment assigned to {len(valid_batch_ids)} batch(es)"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
