"""
Teacher-Specific Assessment Operations
Handles teacher analytics, question management, and assessment administration
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
import logging
from ...db import get_db
from ...schemas.schemas import (
    QuestionCreate, QuestionResponse, CodingQuestionCreate, CodingQuestionResponse,
    AssessmentResponse, StudentNotification
)
from ...dependencies import require_teacher, get_current_user
from ...models.models import UserModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/assessments/teacher", tags=["assessments-teacher"])

@router.post("/{assessment_id}/assign-batches")
async def assign_teacher_assessment_to_batches(
    assessment_id: str,
    batch_ids: List[str],
    user: UserModel = Depends(require_teacher)
):
    """Assign a teacher-created assessment to batches and notify students."""
    try:
        print(f"🔔 [ASSIGN-BATCHES] Starting batch assignment for assessment {assessment_id}")
        print(f"🔔 [ASSIGN-BATCHES] Teacher: {user.email} (ID: {user.id})")
        print(f"🔔 [ASSIGN-BATCHES] Batch IDs to assign: {batch_ids}")
        
        db = await get_db()

        if not ObjectId.is_valid(assessment_id):
            print(f"❌ [ASSIGN-BATCHES] Invalid assessment ID: {assessment_id}")
            raise HTTPException(status_code=400, detail="Invalid assessment ID")

        print(f"🔍 [ASSIGN-BATCHES] Looking for assessment {assessment_id} owned by teacher {user.id}")
        
        assessment = await db.teacher_assessments.find_one({
            "_id": ObjectId(assessment_id),
            "teacher_id": str(user.id)
        })
        if not assessment:
            print(f"🔍 [ASSIGN-BATCHES] Assessment not found with string teacher_id, trying ObjectId...")
            # Try with ObjectId comparison as well
            assessment = await db.teacher_assessments.find_one({
                "_id": ObjectId(assessment_id),
                "teacher_id": ObjectId(user.id)
            })
        if not assessment:
            print(f"❌ [ASSIGN-BATCHES] Assessment not found or access denied")
            raise HTTPException(status_code=404, detail="Assessment not found or access denied")

        print(f"✅ [ASSIGN-BATCHES] Found assessment: {assessment.get('title', 'Untitled')}")
        print(f"📝 [ASSIGN-BATCHES] Assessment details: ID={assessment_id}, Title={assessment.get('title')}, Topic={assessment.get('topic')}")

        await db.teacher_assessments.update_one(
            {"_id": ObjectId(assessment_id)},
            {"$set": {"batches": batch_ids}}
        )
        print(f"✅ [ASSIGN-BATCHES] Updated assessment with batch IDs: {batch_ids}")

        notifications: List[Dict[str, Any]] = []
        total_students_notified = 0
        
        for batch_id in batch_ids:
            print(f"🔍 [ASSIGN-BATCHES] Processing batch: {batch_id}")
            
            if not ObjectId.is_valid(batch_id):
                print(f"❌ [ASSIGN-BATCHES] Invalid batch ID: {batch_id}")
                continue
                
            batch = await db.batches.find_one({"_id": ObjectId(batch_id)})
            if not batch:
                print(f"❌ [ASSIGN-BATCHES] Batch not found: {batch_id}")
                continue
                
            print(f"✅ [ASSIGN-BATCHES] Found batch: {batch.get('name', 'Unknown')}")
            student_ids = batch.get("student_ids", [])
            print(f"👥 [ASSIGN-BATCHES] Batch has {len(student_ids)} students: {student_ids}")
            
            for student_id in student_ids:
                print(f"🔔 [ASSIGN-BATCHES] Creating notification for student: {student_id}")
                
                notification = {
                    "student_id": student_id,
                    "type": "assessment_assigned",
                    "title": f"New Assessment: {assessment.get('title', 'Untitled')}",
                    "message": f"A new {assessment.get('difficulty', 'medium')} assessment on {assessment.get('topic', 'General')} has been assigned to you.",
                    "assessment_id": assessment_id,
                    "created_at": datetime.utcnow(),
                    "is_read": False
                }
                notifications.append(notification)
                total_students_notified += 1
                print(f"📝 [ASSIGN-BATCHES] Notification created: {notification['title']}")

        print(f"📊 [ASSIGN-BATCHES] Total notifications to create: {len(notifications)}")
        print(f"👥 [ASSIGN-BATCHES] Total students to notify: {total_students_notified}")

        if notifications:
            result = await db.notifications.insert_many(notifications)
            print(f"✅ [ASSIGN-BATCHES] Inserted {len(result.inserted_ids)} notifications successfully")
            print(f"📝 [ASSIGN-BATCHES] Notification IDs: {[str(id) for id in result.inserted_ids]}")
        else:
            print(f"⚠️ [ASSIGN-BATCHES] No notifications created - no students found in batches")

        return {"success": True, "message": f"Batches assigned and {total_students_notified} students notified"}

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ [ASSIGN-BATCHES] Error: {str(e)}")
        import traceback
        print(f"❌ [ASSIGN-BATCHES] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{assessment_id}/publish")
async def publish_teacher_assessment(
    assessment_id: str,
    user: UserModel = Depends(require_teacher)
):
    """Publish a teacher-created assessment and notify assigned batches."""
    try:
        print(f"📢 [PUBLISH] Starting publish for assessment {assessment_id}")
        print(f"📢 [PUBLISH] Teacher: {user.email} (ID: {user.id})")
        
        db = await get_db()

        if not ObjectId.is_valid(assessment_id):
            print(f"❌ [PUBLISH] Invalid assessment ID: {assessment_id}")
            raise HTTPException(status_code=400, detail="Invalid assessment ID")

        print(f"🔍 [PUBLISH] Looking for assessment {assessment_id} owned by teacher {user.id}")
        
        assessment = await db.teacher_assessments.find_one({
            "_id": ObjectId(assessment_id),
            "teacher_id": str(user.id)
        })
        if not assessment:
            print(f"🔍 [PUBLISH] Assessment not found with string teacher_id, trying ObjectId...")
            # Try with ObjectId comparison as well
            assessment = await db.teacher_assessments.find_one({
                "_id": ObjectId(assessment_id),
                "teacher_id": ObjectId(user.id)
            })
        if not assessment:
            print(f"❌ [PUBLISH] Assessment not found or access denied")
            raise HTTPException(status_code=404, detail="Assessment not found or access denied")

        print(f"✅ [PUBLISH] Found assessment: {assessment.get('title', 'Untitled')}")
        
        questions = assessment.get("questions", [])
        print(f"📝 [PUBLISH] Assessment has {len(questions)} questions")
        
        if len(questions) == 0:
            print(f"❌ [PUBLISH] Assessment has no questions, cannot publish")
            raise HTTPException(status_code=400, detail="Assessment must have at least one question to publish")

        await db.teacher_assessments.update_one(
            {"_id": ObjectId(assessment_id)},
            {"$set": {"status": "active", "is_active": True, "published_at": datetime.utcnow()}}
        )
        print(f"✅ [PUBLISH] Updated assessment status to active and published")

        batch_ids = assessment.get("batches", [])
        print(f"🔍 [PUBLISH] Assessment assigned to batches: {batch_ids}")
        
        notifications: List[Dict[str, Any]] = []
        total_students_notified = 0
        
        for batch_id in batch_ids:
            print(f"🔍 [PUBLISH] Processing batch: {batch_id}")
            
            if not ObjectId.is_valid(batch_id):
                print(f"❌ [PUBLISH] Invalid batch ID: {batch_id}")
                continue
                
            batch = await db.batches.find_one({"_id": ObjectId(batch_id)})
            if not batch:
                print(f"❌ [PUBLISH] Batch not found: {batch_id}")
                continue
                
            print(f"✅ [PUBLISH] Found batch: {batch.get('name', 'Unknown')}")
            student_ids = batch.get("student_ids", [])
            print(f"👥 [PUBLISH] Batch has {len(student_ids)} students: {student_ids}")
            
            for student_id in student_ids:
                print(f"🔔 [PUBLISH] Creating notification for student: {student_id}")
                
                notification = {
                    "student_id": student_id,
                    "type": "assessment_assigned",
                    "title": f"New Assessment: {assessment.get('title', 'Untitled')}",
                    "message": f"A new {assessment.get('difficulty', 'medium')} assessment on {assessment.get('topic', 'General')} has been assigned to you.",
                    "assessment_id": assessment_id,
                    "created_at": datetime.utcnow(),
                    "is_read": False
                }
                notifications.append(notification)
                total_students_notified += 1
                print(f"📝 [PUBLISH] Notification created: {notification['title']}")

        print(f"📊 [PUBLISH] Total notifications to create: {len(notifications)}")
        print(f"👥 [PUBLISH] Total students to notify: {total_students_notified}")

        if notifications:
            result = await db.notifications.insert_many(notifications)
            print(f"✅ [PUBLISH] Inserted {len(result.inserted_ids)} notifications successfully")
            print(f"📝 [PUBLISH] Notification IDs: {[str(id) for id in result.inserted_ids]}")
        else:
            print(f"⚠️ [PUBLISH] No notifications created - no students found in batches")

        return {"success": True, "message": f"Assessment published successfully and {total_students_notified} students notified"}

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ [PUBLISH] Error: {str(e)}")
        import traceback
        print(f"❌ [PUBLISH] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))
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
        logger.info(f"🔍 [STUDENT-RESULTS] Getting results for student: {student_id}, teacher: {user.email}")
        db = await get_db()
        
        if not ObjectId.is_valid(student_id):
            logger.error(f"❌ [STUDENT-RESULTS] Invalid student ID: {student_id}")
            raise HTTPException(status_code=400, detail="Invalid student ID")
        
        # Verify student belongs to teacher's batch
        logger.info(f"🔍 [STUDENT-RESULTS] Looking for student in database...")
        student = await db.users.find_one({
            "_id": ObjectId(student_id),
            "role": "student"
        })
        
        if not student:
            logger.error(f"❌ [STUDENT-RESULTS] Student not found: {student_id}")
            raise HTTPException(status_code=404, detail="Student not found")
        
        logger.info(f"✅ [STUDENT-RESULTS] Student found: {student.get('email', 'Unknown')}")
        
        # Check if student is in teacher's batch
        batch_id = student.get("batch_id")
        logger.info(f"🔍 [STUDENT-RESULTS] Student batch_id: {batch_id}, type: {type(batch_id)}")
        
        if not batch_id:
            logger.error(f"❌ [STUDENT-RESULTS] Student has no batch_id")
            raise HTTPException(status_code=403, detail="Student not assigned to any batch")
        
        # Ensure batch_id is an ObjectId
        if isinstance(batch_id, str):
            if not ObjectId.is_valid(batch_id):
                logger.error(f"❌ [STUDENT-RESULTS] Invalid batch_id string: {batch_id}")
                raise HTTPException(status_code=403, detail="Invalid batch assignment")
            batch_id = ObjectId(batch_id)
        
        student_batch = await db.batches.find_one({
            "_id": batch_id,
            "teacher_id": str(user.id)
        })
        
        logger.info(f"🔍 [STUDENT-RESULTS] Batch query result: {student_batch is not None}")
        
        if not student_batch:
            logger.error(f"❌ [STUDENT-RESULTS] Student's batch not found or not owned by teacher")
            raise HTTPException(status_code=403, detail="Access denied - student not in your batch")
        
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
        
        # Handle last_activity - it could be datetime, string, or None
        last_activity = student.get("last_activity", datetime.utcnow())
        if isinstance(last_activity, datetime):
            last_activity_str = last_activity.isoformat()
        elif isinstance(last_activity, str):
            last_activity_str = last_activity
        else:
            last_activity_str = datetime.utcnow().isoformat()
        
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
                "last_activity": last_activity_str
            },
            "results": all_results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [STUDENT-RESULTS] Unexpected error: {type(e).__name__}: {str(e)}", exc_info=True)
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

@router.get("/teacher/{assessment_id}")
async def get_teacher_assessment_info(
    assessment_id: str,
    user: UserModel = Depends(get_current_user)
):
    """Get basic assessment information for teachers"""
    try:
        db = await get_db()
        
        if not ObjectId.is_valid(assessment_id):
            raise HTTPException(status_code=400, detail="Invalid assessment ID")
        
        # Try to find in assessments collection
        assessment = await db.assessments.find_one({"_id": ObjectId(assessment_id)})
        
        # Try teacher_assessments collection if not found
        if not assessment:
            assessment = await db.teacher_assessments.find_one({"_id": ObjectId(assessment_id)})
        
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        # Build response
        return {
            "id": str(assessment["_id"]),
            "title": assessment.get("title", "Untitled Assessment"),
            "subject": assessment.get("subject", assessment.get("topic", "General")),
            "difficulty": assessment.get("difficulty", "medium"),
            "description": assessment.get("description", ""),
            "time_limit": assessment.get("time_limit", 30),
            "question_count": assessment.get("question_count", len(assessment.get("questions", []))),
            "questions": assessment.get("questions", []),
            "created_at": assessment.get("created_at", datetime.utcnow()).isoformat(),
            "status": assessment.get("status", "draft"),
            "is_active": assessment.get("is_active", False)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{assessment_id}/results")
async def get_assessment_results_list(
    assessment_id: str,
    user: UserModel = Depends(get_current_user)
):
    """Get list of all student results for an assessment - for teachers"""
    try:
        db = await get_db()
        
        print(f"📊 [RESULTS] Getting results for assessment: {assessment_id}, user: {user.email}, role: {user.role}")
        
        # Check if user is teacher or admin
        if user.role not in ["teacher", "admin"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get submissions from both collections
        submissions = []
        
        # Get from assessment_submissions (regular assessments)
        try:
            regular_subs = await db.assessment_submissions.find({
                "assessment_id": assessment_id
            }).to_list(length=None)
            print(f"📊 [RESULTS] Found {len(regular_subs)} regular submissions")
            submissions.extend(regular_subs)
        except Exception as e:
            print(f"⚠️ [RESULTS] Error getting regular submissions: {e}")
            pass
        
        # Get from teacher_assessment_results (teacher-created assessments)
        try:
            teacher_subs = await db.teacher_assessment_results.find({
                "assessment_id": assessment_id
            }).to_list(length=None)
            print(f"📊 [RESULTS] Found {len(teacher_subs)} teacher submissions")
            submissions.extend(teacher_subs)
        except Exception as e:
            print(f"⚠️ [RESULTS] Error getting teacher submissions: {e}")
            pass
        
        # Format results
        results = []
        for sub in submissions:
            try:
                student_id = sub.get("student_id")
                
                # Convert student_id to string if it's an ObjectId
                if isinstance(student_id, ObjectId):
                    student_id_str = str(student_id)
                else:
                    student_id_str = student_id
                
                # Get student info
                student = None
                if student_id:
                    try:
                        # Try with ObjectId first
                        if ObjectId.is_valid(student_id_str):
                            student = await db.users.find_one({"_id": ObjectId(student_id_str)})
                        
                        # If not found and student_id is ObjectId, try direct match
                        if not student and isinstance(student_id, ObjectId):
                            student = await db.users.find_one({"_id": student_id})
                        
                        # If still not found, try string match
                        if not student:
                            student = await db.users.find_one({"_id": student_id_str})
                    except Exception as e:
                        print(f"⚠️ [RESULTS] Error getting student {student_id}: {e}")
                        pass
                
                student_name = student.get("full_name", "Unknown") if student else "Unknown"
                student_email = student.get("email", "") if student else ""
                
                # Handle submitted_at safely
                submitted_at = sub.get("submitted_at")
                if submitted_at:
                    if hasattr(submitted_at, 'isoformat'):
                        submitted_at_str = submitted_at.isoformat()
                    else:
                        submitted_at_str = str(submitted_at)
                else:
                    submitted_at_str = datetime.utcnow().isoformat()
                
                results.append({
                    "student_id": student_id_str,
                    "student_name": student_name,
                    "student_email": student_email,
                    "score": sub.get("score", 0),
                    "total_questions": sub.get("total_questions", 0),
                    "percentage": sub.get("percentage", 0),
                    "time_taken": sub.get("time_taken", 0),
                    "submitted_at": submitted_at_str
                })
            except Exception as e:
                print(f"⚠️ [RESULTS] Error formatting submission: {e}")
                continue
        
        print(f"✅ [RESULTS] Returning {len(results)} results")
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ [RESULTS] Error getting results: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{assessment_id}/assigned-students")
async def get_assigned_students_with_results(
    assessment_id: str,
    user: UserModel = Depends(get_current_user)
):
    """Get list of assigned students with their submission status"""
    try:
        db = await get_db()
        
        # Check if user is teacher or admin
        if user.role not in ["teacher", "admin"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        if not ObjectId.is_valid(assessment_id):
            raise HTTPException(status_code=400, detail="Invalid assessment ID")
        
        # Get assessment
        assessment = await db.assessments.find_one({"_id": ObjectId(assessment_id)})
        if not assessment:
            assessment = await db.teacher_assessments.find_one({"_id": ObjectId(assessment_id)})
        
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        # Get assigned batches
        batch_ids = assessment.get("assigned_batches", assessment.get("batches", []))
        
        # Get students from batches
        assigned_students = []
        for batch_id_str in batch_ids:
            try:
                batch = await db.batches.find_one({"_id": ObjectId(batch_id_str)})
                if batch:
                    student_ids = batch.get("student_ids", [])
                    for student_id in student_ids:
                        try:
                            student = await db.users.find_one({"_id": ObjectId(student_id)})
                            if student:
                                # Check if student has submitted
                                submission = await db.assessment_submissions.find_one({
                                    "assessment_id": assessment_id,
                                    "student_id": student_id
                                })
                                if not submission:
                                    submission = await db.teacher_assessment_results.find_one({
                                        "assessment_id": assessment_id,
                                        "student_id": student_id
                                    })
                                
                                assigned_students.append({
                                    "student_id": str(student["_id"]),
                                    "student_name": student.get("full_name", "Unknown"),
                                    "student_email": student.get("email", ""),
                                    "submitted": submission is not None,
                                    "score": submission.get("score", 0) if submission else 0,
                                    "total_questions": submission.get("total_questions", 0) if submission else 0,
                                    "percentage": submission.get("percentage", 0) if submission else 0,
                                    "time_taken": submission.get("time_taken", 0) if submission else 0,
                                    "submitted_at": submission.get("submitted_at", None).isoformat() if submission and submission.get("submitted_at") else None,
                                    "result_id": str(submission["_id"]) if submission else None
                                })
                        except Exception as e:
                            print(f"Error processing student {student_id}: {e}")
                            continue
            except Exception as e:
                print(f"Error processing batch {batch_id_str}: {e}")
                continue
        
        return assigned_students
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))