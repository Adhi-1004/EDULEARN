"""
Teacher dashboard endpoints
Handles teacher-specific functionality, student management, and educational tools
"""
from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
from bson import ObjectId

from ..core.security import security_manager
from ..db import get_db
from ..schemas.schemas import UserResponse
from ..models.models import UserModel
from ..dependencies import require_teacher_or_admin, require_batch_management, require_analytics_access

router = APIRouter()

# Response Models
class BatchOverviewResponse(BaseModel):
    batch_id: str
    batch_name: str
    total_students: int
    active_students: int
    average_score: float
    completion_rate: float
    health_score: float

class StudentPerformanceResponse(BaseModel):
    student_id: str
    student_name: str
    overall_score: float
    assignments_completed: int
    assignments_total: int
    last_activity: Optional[datetime]
    performance_trend: str
    strengths: List[str]
    weaknesses: List[str]

class TeacherDashboardResponse(BaseModel):
    teacher_id: str
    total_students: int
    active_batches: int
    pending_assignments: int
    recent_activities: List[Dict[str, Any]]
    performance_metrics: Dict[str, Any]

# --- AI Student Reports Models ---
class AIReportModel(BaseModel):
    id: str
    studentId: str
    studentName: str
    generatedAt: str
    summary: str
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    performanceTrend: str
    nextSteps: List[str]

class GenerateReportRequest(BaseModel):
    studentId: str
    teacherId: str

@router.get("/dashboard", response_model=TeacherDashboardResponse)
async def get_teacher_dashboard(current_user: UserModel = Depends(require_teacher_or_admin)):
    """Get teacher dashboard overview"""
    try:
        db = await get_db()
        
        # Get teacher's students (placeholder logic)
        total_students = await db.users.count_documents({"role": "student"})
        active_batches = 3  # Placeholder
        pending_assignments = 5  # Placeholder
        
        # Get recent activities (placeholder)
        recent_activities = [
            {
                "type": "assignment_submitted",
                "student_name": "John Doe",
                "assignment": "Math Quiz 1",
                "timestamp": datetime.utcnow() - timedelta(hours=2)
            },
            {
                "type": "student_registered",
                "student_name": "Jane Smith",
                "timestamp": datetime.utcnow() - timedelta(hours=5)
            }
        ]
        
        # Performance metrics (placeholder)
        performance_metrics = {
            "average_student_score": 85.5,
            "completion_rate": 78.2,
            "engagement_score": 82.1
        }
        
        return TeacherDashboardResponse(
            teacher_id=str(current_user.id),
            total_students=total_students,
            active_batches=active_batches,
            pending_assignments=pending_assignments,
            recent_activities=recent_activities,
            performance_metrics=performance_metrics
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get teacher dashboard: {str(e)}"
        )

@router.get("/batches", response_model=List[BatchOverviewResponse])
async def get_batch_overview(current_user: UserModel = Depends(require_teacher_or_admin)):
    """Get overview of all batches"""
    try:
        db = await get_db()
        
        # Get batches from database
        batches_cursor = db.batches.find({"teacher_id": current_user.id})
        batches = await batches_cursor.to_list(length=100)
        
        batch_overviews = []
        for batch in batches:
            # Count students in this batch (handle both ObjectId and string batch_id)
            student_count = await db.users.count_documents({
                "$or": [
                    {"batch_id": batch["_id"], "role": "student"},
                    {"batch_id": str(batch["_id"]), "role": "student"}
                ]
            })
            
            # Get performance metrics for this batch (handle both ObjectId and string batch_id)
            results_cursor = db.results.find({
                "$or": [
                    {"batch_id": batch["_id"]},
                    {"batch_id": str(batch["_id"])}
                ]
            })
            results = await results_cursor.to_list(length=1000)
            
            if results:
                avg_score = sum(r.get("score", 0) for r in results) / len(results)
                completion_rate = len([r for r in results if r.get("completed", False)]) / len(results) if results else 0
            else:
                avg_score = 0
                completion_rate = 0
            
            batch_overviews.append(BatchOverviewResponse(
                batch_id=str(batch["_id"]),
                batch_name=batch.get("name", "Unnamed Batch"),
                total_students=student_count,
                active_students=student_count,  # Simplified for now
                average_score=avg_score,
                completion_rate=completion_rate,
                health_score=min(1.0, completion_rate * 1.2)  # Simple health calculation
            ))
        
        return batch_overviews
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get batch overview: {str(e)}"
        )

@router.get("/students")
async def get_students(
    batch_id: Optional[str] = Query(None),
    current_user: UserModel = Depends(require_teacher_or_admin)
):
    """Get all students, optionally filtered by batch"""
    try:
        db = await get_db()
        
        # Build query filter
        filter_dict = {"role": "student"}
        if batch_id and batch_id != "all":
            filter_dict["batch_id"] = batch_id
        
        # Get students from database
        students_cursor = db.users.find(filter_dict)
        students = await students_cursor.to_list(length=1000)
        
        # Get student performance data
        student_list = []
        for student in students:
            # Get student's recent results for progress calculation
            results_cursor = db.results.find({"user_id": student["_id"]}).sort("submitted_at", -1).limit(10)
            results = await results_cursor.to_list(length=10)
            
            # Calculate progress (average of last 10 scores)
            if results:
                progress = sum(r.get("score", 0) for r in results) / len(results)
            else:
                progress = 0
            
            # Get last activity
            last_activity = student.get("last_login", student.get("created_at", ""))
            
            student_list.append({
                "id": str(student["_id"]),
                "name": student.get("name") or student.get("username") or "Unknown",
                "email": student.get("email") or "",
                "progress": progress or 0,
                "lastActive": last_activity or "",
                "batch": student.get("batch_name") or "No Batch",
                "batchId": str(student.get("batch_id", "")) if student.get("batch_id") else None
            })
        
        return {"success": True, "students": student_list}
        
    except Exception as e:
        print(f"[ERROR] [TEACHER] Error getting students: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get students: {str(e)}"
        )

@router.get("/students/performance", response_model=List[StudentPerformanceResponse])
async def get_student_performance(
    batch_id: Optional[str] = Query(None),
    current_user: UserModel = Depends(require_teacher_or_admin)
):
    """Get student performance analytics"""
    try:
        db = await get_db()
        
        # Get students (placeholder logic)
        filter_dict = {"role": "student"}
        if batch_id:
            filter_dict["batch_id"] = batch_id
        
        students_cursor = db.users.find(filter_dict).limit(20)
        students = []
        
        async for student_doc in students_cursor:
            # Calculate performance metrics (placeholder)
            overall_score = 75.0 + (hash(str(student_doc["_id"])) % 25)  # Random score between 75-100
            assignments_completed = 8 + (hash(str(student_doc["_id"])) % 5)  # Random between 8-12
            assignments_total = 12
            
            # Determine performance trend
            if overall_score >= 85:
                performance_trend = "excellent"
            elif overall_score >= 75:
                performance_trend = "good"
            elif overall_score >= 65:
                performance_trend = "average"
            else:
                performance_trend = "needs_improvement"
            
            students.append(StudentPerformanceResponse(
                student_id=str(student_doc["_id"]),
                student_name=student_doc.get("username", "Unknown"),
                overall_score=overall_score,
                assignments_completed=assignments_completed,
                assignments_total=assignments_total,
                last_activity=student_doc.get("last_login"),
                performance_trend=performance_trend,
                strengths=["Problem Solving", "Critical Thinking"],
                weaknesses=["Time Management", "Attention to Detail"]
            ))
        
        return students
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get student performance: {str(e)}"
        )

@router.get("/analytics/overview")
async def get_analytics_overview(current_user: UserModel = Depends(require_analytics_access)):
    """Get comprehensive analytics overview"""
    try:
        db = await get_db()
        
        # Get analytics data (placeholder)
        analytics = {
            "student_engagement": {
                "daily_active_users": 45,
                "weekly_active_users": 120,
                "monthly_active_users": 350
            },
            "academic_performance": {
                "average_score": 78.5,
                "pass_rate": 85.2,
                "improvement_rate": 12.3
            },
            "content_analytics": {
                "total_assignments": 25,
                "completed_assignments": 18,
                "average_completion_time": "2.5 hours"
            },
            "trends": {
                "performance_trend": "increasing",
                "engagement_trend": "stable",
                "completion_trend": "improving"
            }
        }
        
        return analytics
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analytics overview: {str(e)}"
        )

@router.post("/batches/{batch_id}/students/{student_id}/feedback")
async def add_student_feedback(
    batch_id: str,
    student_id: str,
    feedback: Dict[str, Any],
    current_user: UserModel = Depends(require_teacher_or_admin)
):
    """Add feedback for a specific student"""
    try:
        db = await get_db()
        
        # Validate student exists
        student = await db.users.find_one({"_id": student_id, "role": "student"})
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
        
        # Store feedback
        feedback_doc = {
            "student_id": student_id,
            "batch_id": batch_id,
            "teacher_id": str(current_user.id),
            "feedback": feedback,
            "created_at": datetime.utcnow()
        }
        
        # Insert feedback (assuming feedback collection exists)
        if hasattr(db, 'feedback'):
            await db.feedback.insert_one(feedback_doc)
        
        return {"message": "Feedback added successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add feedback: {str(e)}"
        )

@router.get("/students/{student_id}/detailed-report")
async def get_student_detailed_report(
    student_id: str,
    current_user: UserModel = Depends(require_teacher_or_admin)
):
    """Get detailed report for a specific student"""
    try:
        db = await get_db()
        
        # Get student
        student = await db.users.find_one({"_id": student_id, "role": "student"})
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
        
        # Generate detailed report (placeholder)
        report = {
            "student_info": {
                "name": student.get("username", "Unknown"),
                "email": student.get("email", ""),
                "joined_date": student.get("created_at"),
                "last_activity": student.get("last_login")
            },
            "academic_performance": {
                "overall_score": 82.5,
                "assignments_completed": 15,
                "assignments_total": 18,
                "average_time_per_assignment": "1.5 hours"
            },
            "learning_analytics": {
                "strengths": ["Mathematics", "Problem Solving"],
                "weaknesses": ["Time Management", "Attention to Detail"],
                "learning_style": "Visual",
                "engagement_level": "High"
            },
            "recommendations": [
                "Focus on time management skills",
                "Practice more problem-solving exercises",
                "Consider additional support for attention to detail"
            ]
        }
        
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get student report: {str(e)}"
        )

# Batch Management Endpoints
class BatchCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None

class BatchResponse(BaseModel):
    success: bool
    batch_id: str
    message: str

@router.post("/batches", response_model=BatchResponse)
async def create_batch(
    batch_data: BatchCreateRequest,
    current_user: UserModel = Depends(require_teacher_or_admin)
):
    """Create a new batch"""
    try:
        db = await get_db()
        
        print(f"[DEBUG] [TEACHER] Creating batch: {batch_data.name}")
        print(f"[DEBUG] [TEACHER] Teacher ID: {current_user.id}")
        
        # Create batch document
        batch_doc = {
            "name": batch_data.name,
            "description": batch_data.description,
            "teacher_id": current_user.id,
            "created_at": datetime.utcnow(),
            "status": "active"
        }
        
        print(f"[DEBUG] [TEACHER] Batch document: {batch_doc}")
        
        # Insert batch
        result = await db.batches.insert_one(batch_doc)
        batch_id = str(result.inserted_id)
        
        print(f"[SUCCESS] [TEACHER] Created batch '{batch_data.name}' with ID: {batch_id}")
        
        return BatchResponse(
            success=True,
            batch_id=batch_id,
            message=f"Batch '{batch_data.name}' created successfully"
        )
        
    except Exception as e:
        print(f"[ERROR] [TEACHER] Error creating batch: {str(e)}")
        import traceback
        print(f"[ERROR] [TEACHER] Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create batch: {str(e)}"
        )

# Student Management Endpoints
class StudentAddRequest(BaseModel):
    email: str
    name: Optional[str] = None
    batch_id: str

class StudentAddResponse(BaseModel):
    success: bool
    message: str
    student_id: Optional[str] = None

class StudentRemoveRequest(BaseModel):
    student_id: str
    batch_id: str

class StudentRemoveResponse(BaseModel):
    success: bool
    message: str

@router.post("/students/add", response_model=StudentAddResponse)
async def add_student_to_batch(
    student_data: StudentAddRequest,
    current_user: UserModel = Depends(require_teacher_or_admin)
):
    """Add a student to a batch"""
    try:
        db = await get_db()
        
        print(f"[DEBUG] [TEACHER] Adding student {student_data.email} to batch {student_data.batch_id}")
        
        # Convert batch_id to ObjectId for MongoDB query
        try:
            batch_object_id = ObjectId(student_data.batch_id)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid batch ID format"
            )
        
        # Check if batch exists and belongs to teacher
        batch = await db.batches.find_one({
            "_id": batch_object_id,
            "teacher_id": current_user.id
        })
        
        if not batch:
            print(f"[ERROR] [TEACHER] Batch {student_data.batch_id} not found or not owned by teacher {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Batch not found or you don't have permission to add students to this batch"
            )
        
        print(f"[SUCCESS] [TEACHER] Found batch: {batch['name']}")
        
        # Check if student exists
        student = await db.users.find_one({"email": student_data.email, "role": "student"})
        
        if not student:
            # Create new student if they don't exist
            student_doc = {
                "email": student_data.email,
                "name": student_data.name or student_data.email.split("@")[0],
                "role": "student",
                "batch_id": ObjectId(student_data.batch_id),
                "batch_name": batch["name"],
                "created_at": datetime.utcnow(),
                "is_active": True,
                "password": "temp_password_123"  # Temporary password, student should change on first login
            }
            
            result = await db.users.insert_one(student_doc)
            student_id = str(result.inserted_id)
            
            # Add student to batch's student_ids array
            await db.batches.update_one(
                {"_id": ObjectId(student_data.batch_id)},
                {"$addToSet": {"student_ids": student_id}}
            )
            
            # Create notification for the student
            notification = {
                "user_id": ObjectId(student_id),
                "type": "batch_assignment",
                "title": f"Added to Batch: {batch['name']}",
                "message": f"You have been added to batch '{batch['name']}' by {current_user.username or 'your teacher'}. Welcome to the class!",
                "batch_id": ObjectId(student_data.batch_id),
                "teacher_id": ObjectId(current_user.id),
                "created_at": datetime.utcnow(),
                "is_read": False,
                "priority": "normal"
            }
            await db.notifications.insert_one(notification)
            
            print(f"[SUCCESS] [TEACHER] Created new student '{student_data.email}' and added to batch '{batch['name']}'")
            print(f"[SUCCESS] [TEACHER] Notification sent to student about batch assignment")
            
            return StudentAddResponse(
                success=True,
                message=f"New student created and added to batch '{batch['name']}'",
                student_id=student_id
            )
        else:
            # Update existing student's batch
            await db.users.update_one(
                {"_id": student["_id"]},
                {
                    "$set": {
                        "batch_id": ObjectId(student_data.batch_id),
                        "batch_name": batch["name"],
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # Add student to batch's student_ids array
            await db.batches.update_one(
                {"_id": ObjectId(student_data.batch_id)},
                {"$addToSet": {"student_ids": str(student["_id"])}}
            )
            
            # Create notification for the existing student
            notification = {
                "user_id": student["_id"],
                "type": "batch_assignment",
                "title": f"Added to Batch: {batch['name']}",
                "message": f"You have been added to batch '{batch['name']}' by {current_user.username or 'your teacher'}. Welcome to the class!",
                "batch_id": ObjectId(student_data.batch_id),
                "teacher_id": ObjectId(current_user.id),
                "created_at": datetime.utcnow(),
                "is_read": False,
                "priority": "normal"
            }
            await db.notifications.insert_one(notification)
            
            print(f"[SUCCESS] [TEACHER] Added existing student '{student_data.email}' to batch '{batch['name']}'")
            print(f"[SUCCESS] [TEACHER] Notification sent to student about batch assignment")
            
            return StudentAddResponse(
                success=True,
                message=f"Student added to batch '{batch['name']}'",
                student_id=str(student["_id"])
            )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] [TEACHER] Error adding student to batch: {str(e)}")
        import traceback
        print(f"[ERROR] [TEACHER] Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add student to batch: {str(e)}"
        )

@router.post("/students/remove", response_model=StudentRemoveResponse)
async def remove_student_from_batch(
    student_data: StudentRemoveRequest,
    current_user: UserModel = Depends(require_teacher_or_admin)
):
    """
    Remove a student from a batch.
    """
    try:
        print(f"[DEBUG] [TEACHER] Removing student {student_data.student_id} from batch {student_data.batch_id}")
        
        # Get database connection
        db = await get_db()
        
        # Validate batch exists and teacher has access
        batch = await db.batches.find_one({"_id": ObjectId(student_data.batch_id)})
        if not batch:
            print(f"[ERROR] [TEACHER] Batch {student_data.batch_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Batch not found"
            )
        
        # Check if teacher owns this batch
        batch_teacher_id = batch.get("teacher_id")
        if batch_teacher_id:
            # Convert to string for comparison if it's an ObjectId
            if hasattr(batch_teacher_id, '__str__'):
                batch_teacher_id = str(batch_teacher_id)
        
        if batch_teacher_id != str(current_user.id):
            print(f"[ERROR] [TEACHER] Teacher {current_user.id} does not own batch {student_data.batch_id}. Batch owner: {batch_teacher_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to modify this batch"
            )
        
        # Validate student exists
        student = await db.users.find_one({"_id": ObjectId(student_data.student_id)})
        if not student:
            print(f"[ERROR] [TEACHER] Student {student_data.student_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
        
        # Check if student is actually in this batch
        student_batch_id = student.get("batch_id")
        if student_batch_id:
            # Convert to string for comparison if it's an ObjectId
            if hasattr(student_batch_id, '__str__'):
                student_batch_id = str(student_batch_id)
        
        if student_batch_id != student_data.batch_id:
            print(f"[ERROR] [TEACHER] Student {student_data.student_id} is not in batch {student_data.batch_id}. Student is in batch: {student_batch_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student is not in this batch"
            )
        
        # Remove student from batch
        await db.users.update_one(
            {"_id": ObjectId(student_data.student_id)},
            {
                "$unset": {
                    "batch_id": "",
                    "batch_name": ""
                },
                "$set": {
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Remove student from batch's student list
        await db.batches.update_one(
            {"_id": ObjectId(student_data.batch_id)},
            {
                "$pull": {"student_ids": student_data.student_id},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        # Create notification for the student about removal
        notification = {
            "user_id": ObjectId(student_data.student_id),
            "type": "batch_removal",
            "title": f"Removed from Batch: {batch['name']}",
            "message": f"You have been removed from batch '{batch['name']}' by {current_user.username or 'your teacher'}. Contact your teacher if this was a mistake.",
            "batch_id": ObjectId(student_data.batch_id),
            "teacher_id": ObjectId(current_user.id),
            "created_at": datetime.utcnow(),
            "is_read": False,
            "priority": "normal"
        }
        await db.notifications.insert_one(notification)
        
        print(f"[SUCCESS] [TEACHER] Removed student '{student.get('name', 'Unknown')}' from batch '{batch['name']}'")
        print(f"[SUCCESS] [TEACHER] Notification sent to student about batch removal")
        
        return StudentRemoveResponse(
            success=True,
            message=f"Student removed from batch '{batch['name']}'"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] [TEACHER] Error removing student from batch: {str(e)}")
        import traceback
        print(f"[ERROR] [TEACHER] Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove student from batch: {str(e)}"
        )

@router.get("/health")
async def teacher_health_check():
    """Health check endpoint for teacher router"""
    return {
        "status": "healthy",
        "message": "Teacher router is working",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/test-batch-creation")
async def test_batch_creation(current_user: UserModel = Depends(require_teacher_or_admin)):
    """Test endpoint to verify batch creation functionality"""
    try:
        db = await get_db()
        
        # Test creating a sample batch
        test_batch = {
            "name": "Test Batch",
            "description": "Test batch for debugging",
            "teacher_id": current_user.id,
            "created_at": datetime.utcnow(),
            "status": "active"
        }
        
        result = await db.batches.insert_one(test_batch)
        batch_id = str(result.inserted_id)
        
        return {
            "success": True,
            "message": "Batch creation test successful",
            "batch_id": batch_id,
            "teacher_id": current_user.id
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Batch creation test failed: {str(e)}",
            "error": str(e)
        }

@router.get("/test-student-creation")
async def test_student_creation(current_user: UserModel = Depends(require_teacher_or_admin)):
    """Test endpoint to verify student creation functionality"""
    try:
        db = await get_db()
        
        # Test creating a sample student
        test_student = {
            "email": "test@example.com",
            "name": "Test Student",
            "role": "student",
            "batch_id": "test_batch_id",
            "batch_name": "Test Batch",
            "created_at": datetime.utcnow(),
            "is_active": True,
            "password": "temp_password_123"
        }
        
        result = await db.users.insert_one(test_student)
        student_id = str(result.inserted_id)
        
        return {
            "success": True,
            "message": "Student creation test successful",
            "student_id": student_id
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Student creation test failed: {str(e)}",
            "error": str(e)
        }

# --- AI Student Reports Endpoints ---
@router.get("/ai-reports/{teacher_id}")
async def get_ai_reports(teacher_id: str, current_user: UserModel = Depends(require_teacher_or_admin)):
    """Return AI reports for a teacher's students (simple stub using stored docs if present)."""
    try:
        db = await get_db()
        # Try to read stored reports if collection exists
        reports = []
        if hasattr(db, 'ai_student_reports'):
            cursor = db.ai_student_reports.find({"teacherId": teacher_id})
            docs = await cursor.to_list(length=1000)
            for d in docs:
                reports.append({
                    "id": str(d.get("_id")),
                    "studentId": d.get("studentId"),
                    "studentName": d.get("studentName"),
                    "generatedAt": (d.get("generatedAt") or datetime.utcnow()).isoformat(),
                    "summary": d.get("summary", ""),
                    "strengths": d.get("strengths", []),
                    "weaknesses": d.get("weaknesses", []),
                    "recommendations": d.get("recommendations", []),
                    "performanceTrend": d.get("performanceTrend", "stable"),
                    "nextSteps": d.get("nextSteps", []),
                })
        return reports
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch AI reports: {str(e)}")


@router.post("/generate-student-report")
async def generate_student_report(payload: GenerateReportRequest, current_user: UserModel = Depends(require_teacher_or_admin)):
    """Generate and persist a simple AI report document for a student (placeholder logic)."""
    try:
        db = await get_db()

        # Fetch student for name/email
        student = await db.users.find_one({"_id": payload.studentId})
        student_name = student.get("name") or student.get("username") or "Unknown Student" if student else "Unknown Student"

        report_doc = {
            "teacherId": payload.teacherId,
            "studentId": payload.studentId,
            "studentName": student_name,
            "generatedAt": datetime.utcnow(),
            "summary": f"{student_name} is showing consistent progress across recent assessments.",
            "strengths": ["Problem Solving", "Consistency"],
            "weaknesses": ["Time Management"],
            "recommendations": ["Practice timed quizzes", "Revise past mistakes"],
            "performanceTrend": "improving",
            "nextSteps": ["Complete 3 practice sets", "Review key concepts"],
        }

        inserted_id = None
        if hasattr(db, 'ai_student_reports'):
            res = await db.ai_student_reports.insert_one(report_doc)
            inserted_id = str(res.inserted_id)

        response = {
            "success": True,
            "report": {
                "id": inserted_id or str(ObjectId()),
                "studentId": report_doc["studentId"],
                "studentName": report_doc["studentName"],
                "generatedAt": report_doc["generatedAt"].isoformat(),
                "summary": report_doc["summary"],
                "strengths": report_doc["strengths"],
                "weaknesses": report_doc["weaknesses"],
                "recommendations": report_doc["recommendations"],
                "performanceTrend": report_doc["performanceTrend"],
                "nextSteps": report_doc["nextSteps"],
            }
        }
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate student report: {str(e)}")

# Teacher Assessment Management
class TeacherAssessmentCreate(BaseModel):
    title: str
    topic: str
    difficulty: str
    question_count: int
    batches: List[str]
    type: str = "ai_generated"

class TeacherAssessmentResponse(BaseModel):
    success: bool
    assessment_id: str
    message: str

@router.post("/assessments/create", response_model=TeacherAssessmentResponse)
async def create_teacher_assessment(
    assessment_data: TeacherAssessmentCreate,
    current_user: UserModel = Depends(require_teacher_or_admin)
):
    """Create an AI-generated assessment for students"""
    try:
        db = await get_db()
        
        print(f"🤖 [TEACHER ASSESSMENT] Creating AI assessment: {assessment_data.title}")
        
        # Generate unique assessment ID
        assessment_id = str(ObjectId())
        
        # Generate questions using Gemini AI
        from app.services.gemini_coding_service import GeminiCodingService
        gemini_service = GeminiCodingService()
        
        generated_questions = await gemini_service.generate_mcq_questions(
            topic=assessment_data.topic,
            difficulty=assessment_data.difficulty,
            count=assessment_data.question_count
        )
        
        # Store in teacher_assessments collection
        teacher_assessment = {
            "_id": ObjectId(assessment_id),
            "title": assessment_data.title,
            "topic": assessment_data.topic,
            "difficulty": assessment_data.difficulty,
            "question_count": assessment_data.question_count,
            "questions": generated_questions,
            "batches": assessment_data.batches,
            "teacher_id": current_user.id,
            "type": assessment_data.type,
            "created_at": datetime.utcnow(),
            "is_active": True,
            "status": "published"
        }
        
        await db.teacher_assessments.insert_one(teacher_assessment)
        
        # Store questions in ai_questions collection for review
        for question in generated_questions:
            # Handle both "answer" and "correct_answer" fields for backward compatibility
            correct_answer = question.get("correct_answer")
            if correct_answer is None and "answer" in question:
                # Convert letter answer (A, B, C, D) to index (0, 1, 2, 3)
                answer_letter = question["answer"].upper()
                if answer_letter in ["A", "B", "C", "D"]:
                    correct_answer = ord(answer_letter) - ord("A")
                else:
                    print(f"⚠️ [WARNING] Invalid answer format: {question['answer']}")
                    continue  # Skip this question
            
            question_doc = {
                "question": question["question"],
                "options": question["options"],
                "correct_answer": correct_answer,
                "explanation": question.get("explanation", ""),
                "topic": assessment_data.topic,
                "difficulty": assessment_data.difficulty,
                "assessment_id": assessment_id,
                "created_at": datetime.utcnow(),
                "source": "teacher_generated"
            }
            await db.ai_questions.insert_one(question_doc)
        
        # Get all students from selected batches
        student_ids = []
        for batch_id in assessment_data.batches:
            batch = await db.batches.find_one({"_id": ObjectId(batch_id)})
            if batch and batch.get("student_ids"):
                # Get students by their IDs from the batch
                batch_student_ids = batch["student_ids"]
                student_ids.extend(batch_student_ids)
                print(f"📢 [TEACHER_ASSESSMENT] Found {len(batch_student_ids)} students in batch {batch_id}")
            else:
                print(f"❌ [TEACHER_ASSESSMENT] No students found in batch {batch_id}")
        
        # Create notifications for students
        notifications = []
        for student_id in student_ids:
            notification = {
                "student_id": student_id,
                "type": "teacher_assessment_assigned",
                "title": f"New Assessment: {assessment_data.title}",
                "message": f"A new {assessment_data.difficulty} assessment on {assessment_data.topic} has been assigned to you.",
                "assessment_id": assessment_id,
                "created_at": datetime.utcnow(),
                "is_read": False
            }
            notifications.append(notification)
        
        if notifications:
            await db.notifications.insert_many(notifications)
        
        print(f"✅ [TEACHER ASSESSMENT] Created assessment {assessment_id} with {len(generated_questions)} questions")
        print(f"📢 [TEACHER ASSESSMENT] Sent {len(notifications)} notifications to students")
        
        return TeacherAssessmentResponse(
            success=True,
            assessment_id=assessment_id,
            message=f"Assessment '{assessment_data.title}' created successfully with {len(generated_questions)} questions"
        )
        
    except Exception as e:
        print(f"❌ [TEACHER ASSESSMENT] Error creating assessment: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create assessment: {str(e)}"
        )