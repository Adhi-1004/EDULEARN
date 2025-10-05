"""
Teacher dashboard endpoints
Handles teacher-specific functionality, student management, and educational tools
"""
from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel

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
            # Count students in this batch
            student_count = await db.users.count_documents({"batch_id": batch["_id"], "role": "student"})
            
            # Get performance metrics for this batch
            results_cursor = db.results.find({"batch_id": batch["_id"]})
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
                "batch": student.get("batch_name") or "No Batch"
            })
        
        return {"success": True, "students": student_list}
        
    except Exception as e:
        print(f"❌ [TEACHER] Error getting students: {str(e)}")
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
        
        # Create batch document
        batch_doc = {
            "name": batch_data.name,
            "description": batch_data.description,
            "teacher_id": current_user.id,
            "created_at": datetime.utcnow(),
            "status": "active"
        }
        
        # Insert batch
        result = await db.batches.insert_one(batch_doc)
        batch_id = str(result.inserted_id)
        
        print(f"✅ [TEACHER] Created batch '{batch_data.name}' with ID: {batch_id}")
        
        return BatchResponse(
            success=True,
            batch_id=batch_id,
            message=f"Batch '{batch_data.name}' created successfully"
        )
        
    except Exception as e:
        print(f"❌ [TEACHER] Error creating batch: {str(e)}")
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

@router.post("/students/add", response_model=StudentAddResponse)
async def add_student_to_batch(
    student_data: StudentAddRequest,
    current_user: UserModel = Depends(require_teacher_or_admin)
):
    """Add a student to a batch"""
    try:
        db = await get_db()
        
        # Check if batch exists and belongs to teacher
        batch = await db.batches.find_one({
            "_id": student_data.batch_id,
            "teacher_id": current_user.id
        })
        
        if not batch:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Batch not found or you don't have permission to add students to this batch"
            )
        
        # Check if student exists
        student = await db.users.find_one({"email": student_data.email, "role": "student"})
        
        if not student:
            # Create new student if they don't exist
            from bson import ObjectId
            student_doc = {
                "email": student_data.email,
                "name": student_data.name or student_data.email.split("@")[0],
                "role": "student",
                "batch_id": student_data.batch_id,
                "batch_name": batch["name"],
                "created_at": datetime.utcnow(),
                "is_active": True
            }
            
            result = await db.users.insert_one(student_doc)
            student_id = str(result.inserted_id)
            
            print(f"✅ [TEACHER] Created new student '{student_data.email}' and added to batch '{batch['name']}'")
            
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
                        "batch_id": student_data.batch_id,
                        "batch_name": batch["name"],
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            print(f"✅ [TEACHER] Added existing student '{student_data.email}' to batch '{batch['name']}'")
            
            return StudentAddResponse(
                success=True,
                message=f"Student added to batch '{batch['name']}'",
                student_id=str(student["_id"])
            )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ [TEACHER] Error adding student to batch: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add student to batch: {str(e)}"
        )
