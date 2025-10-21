"""
Teacher-Specific Assessment Operations
Handles teacher analytics, question management, and assessment administration
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from ...db import get_db
from ...schemas.schemas import (
    QuestionCreate, QuestionResponse, CodingQuestionCreate, CodingQuestionResponse,
    AssessmentResponse, StudentNotification
)
from ...dependencies import require_teacher, get_current_user
from ...models.models import UserModel

router = APIRouter(prefix="/assessments", tags=["assessments-teacher"])

@router.get("/teacher/class-performance")
async def get_class_performance_overview(user: UserModel = Depends(require_teacher)):
    """Get overall class performance analytics for teacher"""
    try:
        db = await get_db()
        
        # Get teacher's batches
        batches = await db.batches.find({"teacher_id": str(user.id)}).to_list(length=None)
        batch_ids = [str(batch["_id"]) for batch in batches]
        
        if not batch_ids:
            return {
                "total_students": 0,
                "total_assessments": 0,
                "average_performance": 0,
                "recent_submissions": [],
                "batch_performance": []
            }
        
        # Get all students in teacher's batches
        students = await db.users.find({
            "batch_id": {"$in": [ObjectId(bid) for bid in batch_ids]},
            "role": "student"
        }).to_list(length=None)
        
        student_ids = [str(student["_id"]) for student in students]
        
        # Get submissions from these students
        submissions = await db.assessment_submissions.find({
            "student_id": {"$in": student_ids}
        }).sort("submitted_at", -1).limit(50).to_list(length=None)
        
        # Calculate performance metrics
        total_submissions = len(submissions)
        if total_submissions > 0:
            average_performance = sum(sub["percentage"] for sub in submissions) / total_submissions
        else:
            average_performance = 0
        
        # Get batch-wise performance
        batch_performance = []
        for batch in batches:
            batch_students = [s for s in students if str(s.get("batch_id")) == str(batch["_id"])]
            batch_student_ids = [str(s["_id"]) for s in batch_students]
            
            batch_submissions = [s for s in submissions if s["student_id"] in batch_student_ids]
            
            if batch_submissions:
                batch_avg = sum(sub["percentage"] for sub in batch_submissions) / len(batch_submissions)
            else:
                batch_avg = 0
            
            batch_performance.append({
                "batch_id": str(batch["_id"]),
                "batch_name": batch["name"],
                "student_count": len(batch_students),
                "average_performance": round(batch_avg, 2),
                "total_submissions": len(batch_submissions)
            })
        
        # Get recent submissions
        recent_submissions = []
        for submission in submissions[:10]:  # Last 10 submissions
            student = next((s for s in students if str(s["_id"]) == submission["student_id"]), None)
            if student:
                recent_submissions.append({
                    "student_name": student.get("username", student.get("email", "Unknown")),
                    "assessment_id": submission["assessment_id"],
                    "score": submission["score"],
                    "percentage": submission["percentage"],
                    "submitted_at": submission["submitted_at"].isoformat()
                })
        
        return {
            "total_students": len(students),
            "total_assessments": len(await db.assessments.find({"created_by": str(user.id)}).to_list(length=None)),
            "average_performance": round(average_performance, 2),
            "recent_submissions": recent_submissions,
            "batch_performance": batch_performance
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/teacher/student-results/{student_id}")
async def get_student_detailed_results(
    student_id: str,
    user: UserModel = Depends(require_teacher)
):
    """Get detailed results for a specific student"""
    try:
        db = await get_db()
        
        if not ObjectId.is_valid(student_id):
            raise HTTPException(status_code=400, detail="Invalid student ID")
        
        # Verify student belongs to teacher's batch
        student = await db.users.find_one({
            "_id": ObjectId(student_id),
            "role": "student"
        })
        
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Check if student is in teacher's batch
        student_batch = await db.batches.find_one({
            "_id": student.get("batch_id"),
            "teacher_id": str(user.id)
        })
        
        if not student_batch:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get student's submissions
        submissions = await db.assessment_submissions.find({
            "student_id": student_id
        }).sort("submitted_at", -1).to_list(length=None)
        
        # Get teacher assessment results
        teacher_submissions = await db.teacher_assessment_results.find({
            "student_id": student_id
        }).sort("submitted_at", -1).to_list(length=None)
        
        # Combine and format results
        all_results = []
        
        for submission in submissions:
            # Get assessment details
            assessment = await db.assessments.find_one({"_id": ObjectId(submission["assessment_id"])})
            if assessment:
                all_results.append({
                    "assessment_id": submission["assessment_id"],
                    "assessment_title": assessment["title"],
                    "subject": assessment["subject"],
                    "difficulty": assessment["difficulty"],
                    "score": submission["score"],
                    "percentage": submission["percentage"],
                    "time_taken": submission["time_taken"],
                    "submitted_at": submission["submitted_at"].isoformat(),
                    "total_questions": submission["total_questions"],
                    "answers": submission.get("answers", []),
                    "type": "regular"
                })
        
        for submission in teacher_submissions:
            # Get teacher assessment details
            assessment = await db.teacher_assessments.find_one({"_id": ObjectId(submission["assessment_id"])})
            if assessment:
                all_results.append({
                    "assessment_id": submission["assessment_id"],
                    "assessment_title": assessment["title"],
                    "subject": assessment.get("topic", "General"),
                    "difficulty": assessment["difficulty"],
                    "score": submission["score"],
                    "percentage": submission["percentage"],
                    "time_taken": submission["time_taken"],
                    "submitted_at": submission["submitted_at"].isoformat(),
                    "total_questions": submission["total_questions"],
                    "answers": submission.get("answers", []),
                    "type": "teacher_created"
                })
        
        # Sort by submission date
        all_results.sort(key=lambda x: x["submitted_at"], reverse=True)
        
        # Calculate student statistics
        if all_results:
            avg_percentage = sum(result["percentage"] for result in all_results) / len(all_results)
            total_questions = sum(result["total_questions"] for result in all_results)
            total_score = sum(result["score"] for result in all_results)
        else:
            avg_percentage = 0
            total_questions = 0
            total_score = 0
        
        return {
            "student_info": {
                "id": student_id,
                "name": student.get("username", student.get("email", "Unknown")),
                "email": student["email"],
                "batch_name": student_batch["name"],
                "level": student.get("level", 1),
                "xp": student.get("xp", 0),
                "badges": student.get("badges", [])
            },
            "statistics": {
                "total_assessments": len(all_results),
                "average_percentage": round(avg_percentage, 2),
                "total_questions_answered": total_questions,
                "total_score": total_score,
                "last_activity": student.get("last_activity", datetime.utcnow()).isoformat()
            },
            "results": all_results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/teacher/assessment-analytics/{assessment_id}")
async def get_assessment_analytics(
    assessment_id: str,
    user: UserModel = Depends(require_teacher)
):
    """Get detailed analytics for a specific assessment"""
    try:
        db = await get_db()
        
        if not ObjectId.is_valid(assessment_id):
            raise HTTPException(status_code=400, detail="Invalid assessment ID")
        
        # Get assessment
        assessment = await db.assessments.find_one({
            "_id": ObjectId(assessment_id),
            "created_by": str(user.id)
        })
        
        if not assessment:
            # Try teacher assessments
            assessment = await db.teacher_assessments.find_one({
                "_id": ObjectId(assessment_id),
                "teacher_id": str(user.id)
            })
        
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        # Get submissions
        submissions = await db.assessment_submissions.find({
            "assessment_id": assessment_id
        }).to_list(length=None)
        
        # Get teacher assessment results
        teacher_submissions = await db.teacher_assessment_results.find({
            "assessment_id": assessment_id
        }).to_list(length=None)
        
        # Combine submissions
        all_submissions = submissions + teacher_submissions
        
        if not all_submissions:
            return {
                "assessment_info": {
                    "id": assessment_id,
                    "title": assessment["title"],
                    "subject": assessment.get("subject", assessment.get("topic", "General")),
                    "difficulty": assessment["difficulty"],
                    "question_count": assessment["question_count"],
                    "created_at": assessment["created_at"].isoformat()
                },
                "statistics": {
                    "total_submissions": 0,
                    "average_score": 0,
                    "average_percentage": 0,
                    "completion_rate": 0
                },
                "question_analysis": [],
                "student_performance": []
            }
        
        # Calculate statistics
        total_submissions = len(all_submissions)
        average_score = sum(sub["score"] for sub in all_submissions) / total_submissions
        average_percentage = sum(sub["percentage"] for sub in all_submissions) / total_submissions
        
        # Get assigned students count
        assigned_batches = assessment.get("assigned_batches", assessment.get("batches", []))
        assigned_students = 0
        for batch_id in assigned_batches:
            batch = await db.batches.find_one({"_id": ObjectId(batch_id)})
            if batch:
                assigned_students += len(batch.get("student_ids", []))
        
        completion_rate = (total_submissions / assigned_students * 100) if assigned_students > 0 else 0
        
        # Question analysis
        questions = assessment.get("questions", [])
        question_analysis = []
        
        for i, question in enumerate(questions):
            correct_count = 0
            total_attempts = 0
            
            for submission in all_submissions:
                answers = submission.get("answers", [])
                if i < len(answers):
                    total_attempts += 1
                    if answers[i] == question.get("correct_answer", -1):
                        correct_count += 1
            
            accuracy = (correct_count / total_attempts * 100) if total_attempts > 0 else 0
            
            question_analysis.append({
                "question_number": i + 1,
                "question_text": question.get("question", "N/A"),
                "correct_answer": question.get("correct_answer", -1),
                "total_attempts": total_attempts,
                "correct_attempts": correct_count,
                "accuracy_percentage": round(accuracy, 2)
            })
        
        # Student performance
        student_performance = []
        for submission in all_submissions:
            student_performance.append({
                "student_id": submission["student_id"],
                "student_name": submission["student_name"],
                "score": submission["score"],
                "percentage": submission["percentage"],
                "time_taken": submission["time_taken"],
                "submitted_at": submission["submitted_at"].isoformat()
            })
        
        # Sort by percentage
        student_performance.sort(key=lambda x: x["percentage"], reverse=True)
        
        return {
            "assessment_info": {
                "id": assessment_id,
                "title": assessment["title"],
                "subject": assessment.get("subject", assessment.get("topic", "General")),
                "difficulty": assessment["difficulty"],
                "question_count": assessment["question_count"],
                "created_at": assessment["created_at"].isoformat()
            },
            "statistics": {
                "total_submissions": total_submissions,
                "average_score": round(average_score, 2),
                "average_percentage": round(average_percentage, 2),
                "completion_rate": round(completion_rate, 2),
                "assigned_students": assigned_students
            },
            "question_analysis": question_analysis,
            "student_performance": student_performance
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{assessment_id}/questions", response_model=QuestionResponse)
async def add_question_to_assessment(
    assessment_id: str,
    question_data: QuestionCreate,
    user: UserModel = Depends(require_teacher)
):
    """Add a question to an assessment"""
    try:
        db = await get_db()
        
        if not ObjectId.is_valid(assessment_id):
            raise HTTPException(status_code=400, detail="Invalid assessment ID")
        
        # Verify assessment belongs to teacher
        assessment = await db.assessments.find_one({
            "_id": ObjectId(assessment_id),
            "created_by": str(user.id)
        })
        
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        # Create question document
        question_doc = {
            "question": question_data.question,
            "options": question_data.options,
            "correct_answer": question_data.correct_answer,
            "explanation": question_data.explanation,
            "difficulty": question_data.difficulty,
            "points": question_data.points
        }
        
        # Add question to assessment
        await db.assessments.update_one(
            {"_id": ObjectId(assessment_id)},
            {
                "$push": {"questions": question_doc},
                "$inc": {"question_count": 1}
            }
        )
        
        return QuestionResponse(
            id=str(ObjectId()),
            question=question_data.question,
            options=question_data.options,
            correct_answer=question_data.correct_answer,
            explanation=question_data.explanation,
            points=question_data.points
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{assessment_id}/coding-questions", response_model=CodingQuestionResponse)
async def add_coding_question_to_assessment(
    assessment_id: str,
    question_data: CodingQuestionCreate,
    user: UserModel = Depends(require_teacher)
):
    """Add a coding question to an assessment"""
    try:
        db = await get_db()
        
        if not ObjectId.is_valid(assessment_id):
            raise HTTPException(status_code=400, detail="Invalid assessment ID")
        
        # Verify assessment belongs to teacher
        assessment = await db.assessments.find_one({
            "_id": ObjectId(assessment_id),
            "created_by": str(user.id)
        })
        
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        # Create coding question document
        question_doc = {
            "id": str(ObjectId()),
            "title": question_data.title,
            "description": question_data.description,
            "problem_statement": question_data.problem_statement,
            "constraints": question_data.constraints,
            "examples": question_data.examples,
            "test_cases": question_data.test_cases,
            "hidden_test_cases": question_data.hidden_test_cases,
            "expected_complexity": question_data.expected_complexity,
            "hints": question_data.hints,
            "points": question_data.points,
            "time_limit": question_data.time_limit,
            "memory_limit": question_data.memory_limit
        }
        
        # Add question to assessment
        await db.assessments.update_one(
            {"_id": ObjectId(assessment_id)},
            {
                "$push": {"questions": question_doc},
                "$inc": {"question_count": 1}
            }
        )
        
        return CodingQuestionResponse(
            id=question_doc["id"],
            title=question_data.title,
            description=question_data.description,
            problem_statement=question_data.problem_statement,
            constraints=question_data.constraints,
            examples=question_data.examples,
            hints=question_data.hints,
            points=question_data.points,
            time_limit=question_data.time_limit,
            memory_limit=question_data.memory_limit,
            test_cases=question_data.test_cases
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{assessment_id}/ai-generate-questions")
async def ai_generate_questions(
    assessment_id: str,
    request_data: dict,
    user: UserModel = Depends(require_teacher)
):
    """Generate questions using AI for an assessment"""
    try:
        db = await get_db()
        
        if not ObjectId.is_valid(assessment_id):
            raise HTTPException(status_code=400, detail="Invalid assessment ID")
        
        # Verify assessment belongs to teacher
        assessment = await db.assessments.find_one({
            "_id": ObjectId(assessment_id),
            "created_by": str(user.id)
        })
        
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        topic = request_data.get("topic", assessment["subject"])
        difficulty = request_data.get("difficulty", assessment["difficulty"])
        count = request_data.get("count", 5)
        
        # Generate questions using AI
        from app.services.gemini_coding_service import GeminiCodingService
        gemini_service = GeminiCodingService()
        
        generated_questions = await gemini_service.generate_mcq_questions(
            topic=topic,
            difficulty=difficulty,
            count=count
        )
        
        # Add questions to assessment
        await db.assessments.update_one(
            {"_id": ObjectId(assessment_id)},
            {
                "$push": {"questions": {"$each": generated_questions}},
                "$inc": {"question_count": len(generated_questions)}
            }
        )
        
        return {
            "success": True,
            "message": f"Generated {len(generated_questions)} questions",
            "questions_added": len(generated_questions)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
