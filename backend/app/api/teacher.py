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

@router.get("/batches")
async def get_batch_overview(current_user: UserModel = Depends(require_teacher_or_admin)):
    """Get overview of all batches"""
    try:
        db = await get_db()
        
        print(f"[DEBUG] [TEACHER] Getting batches for teacher: {current_user.id}")
        
        # Get batches from database
        batches_cursor = db.batches.find({"teacher_id": current_user.id})
        batches = await batches_cursor.to_list(length=100)
        
        print(f"[DEBUG] [TEACHER] Found {len(batches)} batches")
        
        batch_list = []
        for batch in batches:
            # Count students in this batch (using batch_ids array)
            batch_id_str = str(batch["_id"])
            student_count = await db.users.count_documents({
                "batch_ids": batch_id_str,
                "role": "student"
            })
            
            # Format created_at
            created_at = batch.get("created_at", datetime.utcnow())
            if hasattr(created_at, 'isoformat'):
                created_at_str = created_at.isoformat()
            else:
                created_at_str = str(created_at)
            
            batch_list.append({
                "id": str(batch["_id"]),
                "name": batch.get("name", "Unnamed Batch"),
                "student_count": student_count,
                "created_at": created_at_str,
                "status": batch.get("status", "active"),
                "description": batch.get("description", "")
            })
        
        print(f"[SUCCESS] [TEACHER] Returning {len(batch_list)} batches")
        return batch_list
        
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
            filter_dict["batch_ids"] = batch_id
        
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
                progress = student.get("average_score", 0)
            
            # Get last activity
            last_activity = student.get("last_activity", student.get("last_login", student.get("created_at", datetime.utcnow())))
            if hasattr(last_activity, 'isoformat'):
                last_activity = last_activity.isoformat()
            else:
                last_activity = str(last_activity)
            
            # Get batch info (multi-batch support)
            batch_ids = student.get("batch_ids", [])
            batch_names_list = []
            
            for bid in batch_ids:
                # Try to get batch name from database
                try:
                    if ObjectId.is_valid(bid):
                        batch_doc = await db.batches.find_one({"_id": ObjectId(bid)})
                    else:
                        batch_doc = await db.batches.find_one({"_id": bid})
                    if batch_doc:
                        batch_names_list.append(batch_doc.get("name", "Unknown"))
                except:
                    pass
            batch_name = ", ".join(batch_names_list) if batch_names_list else "No Batch"
            
            student_list.append({
                "id": str(student["_id"]),
                "name": student.get("full_name") or student.get("username") or student.get("email", "Unknown"),
                "email": student.get("email", ""),
                "progress": round(progress, 2) if progress else 0,
                "lastActive": last_activity,
                "batch": batch_name,
                "batchId": batch_ids[0] if batch_ids else None,  # First batch for backward compatibility
                "batchIds": batch_ids  # All batches (multi-batch support)
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

# -----------------------------
# Delete Batch Endpoint
# -----------------------------
@router.delete("/batches/{batch_id}")
async def delete_batch(batch_id: str, current_user: UserModel = Depends(require_teacher_or_admin)):
    """Delete a batch owned by the current teacher (or any batch if admin).
    Cleans up student references and unassigns assessments from this batch.
    """
    try:
        db = await get_db()

        # Validate ObjectId
        if not ObjectId.is_valid(batch_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid batch id")
        batch_object_id = ObjectId(batch_id)

        # Find batch with ownership check for teachers
        query = {"_id": batch_object_id}
        if current_user.role == "teacher":
            query["teacher_id"] = current_user.id

        batch = await db.batches.find_one(query)
        if not batch:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Batch not found or access denied")

        # Remove batch references from students
        await db.users.update_many({"role": "student", "batch_id": batch_object_id}, {"$unset": {"batch_id": "", "batch_name": ""}})
        await db.users.update_many({"role": "student", "batch_id": batch_id}, {"$unset": {"batch_id": "", "batch_name": ""}})
        await db.users.update_many({"role": "student"}, {"$pull": {"batches": batch_id}})

        # Unassign assessments referencing this batch
        await db.assessments.update_many({}, {"$pull": {"assigned_batches": batch_id}})

        # Delete the batch
        await db.batches.delete_one({"_id": batch_object_id})

        return {"success": True, "message": "Batch deleted successfully", "batch_id": batch_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete batch: {str(e)}")

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
            print(f"[INFO] [TEACHER] Creating new student: {student_data.email}")
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            
            student_doc = {
                "email": student_data.email,
                "username": student_data.name or student_data.email.split("@")[0],
                "full_name": student_data.name or student_data.email.split("@")[0],
                "role": "student",
                "batch_ids": [student_data.batch_id],  # Multi-batch support: use array
                "batch_name": batch["name"],
                "created_at": datetime.utcnow(),
                "last_login": None,
                "last_activity": datetime.utcnow(),
                "is_active": True,
                "password_hash": pwd_context.hash("temppass123"),  # Temporary password
                "level": 1,
                "xp": 0,
                "badges": [],
                "completed_assessments": 0,
                "average_score": 0.0
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
            # Student exists - add to batch (multi-batch support)
            print(f"[INFO] [TEACHER] Student exists: {student_data.email}, adding to batch {batch['name']}")
            
            # Check if student is already in this batch
            student_batch_ids = student.get("batch_ids", [])
            if student_data.batch_id in student_batch_ids:
                return StudentAddResponse(
                    success=True,
                    message=f"Student already exists in batch '{batch['name']}'",
                    student_id=str(student["_id"])
                )
            
            # Add student to new batch (multi-batch support)
            await db.users.update_one(
                {"_id": student["_id"]},
                {
                    "$addToSet": {
                        "batch_ids": student_data.batch_id  # Add to array, prevents duplicates
                    },
                    "$set": {
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
                message=f"Existing student added to batch '{batch['name']}'",
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
        
        # Check if student is actually in this batch (multi-batch support)
        student_batch_ids = student.get("batch_ids", [])
        
        if student_data.batch_id not in student_batch_ids:
            print(f"[ERROR] [TEACHER] Student {student_data.student_id} is not in batch {student_data.batch_id}. Student is in batches: {student_batch_ids}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student is not in this batch"
            )
        
        # Remove student from this batch (multi-batch support)
        await db.users.update_one(
            {"_id": ObjectId(student_data.student_id)},
            {
                "$pull": {
                    "batch_ids": student_data.batch_id  # Remove from array
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
    topic: Optional[str] = None
    difficulty: str
    question_count: Optional[int] = None
    batches: Optional[List[str]] = None
    type: str = "ai_generated"
    # Additional fields for different assessment types
    description: Optional[str] = None
    questions: Optional[List[dict]] = None
    time_limit: Optional[int] = None

class TeacherAssessmentResponse(BaseModel):
    success: bool
    assessment_id: str
    message: str

@router.get("/assessments")
async def get_teacher_assessments(current_user: UserModel = Depends(require_teacher_or_admin)):
    """Get all assessments created by the teacher - fetches from teacher_assessments collection only"""
    try:
        db = await get_db()
        
        # Get teacher assessments from teacher_assessments collection
        # Handle both string and ObjectId teacher_id for backward compatibility
        user_id_str = str(current_user.id)
        user_id_obj = ObjectId(user_id_str) if ObjectId.is_valid(user_id_str) else None
        
        query = {
            "$or": [
                {"teacher_id": user_id_str},
                {"teacher_id": current_user.id}
            ]
        }
        
        if user_id_obj:
            query["$or"].append({"teacher_id": user_id_obj})
        
        assessments = await db.teacher_assessments.find(query).sort("created_at", -1).to_list(length=None)
        
        print(f"📊 [TEACHER ASSESSMENTS] Found {len(assessments)} assessments for teacher {user_id_str}")
        
        # Format assessments
        assessment_list = []
        for assessment in assessments:
            # Count submissions
            submission_count = await db.teacher_assessment_results.count_documents({
                "assessment_id": str(assessment["_id"])
            })
            
            assessment_list.append({
                "id": str(assessment["_id"]),
                "title": assessment["title"],
                "topic": assessment.get("topic", ""),
                "subject": assessment.get("topic", ""),  # Alias for compatibility
                "difficulty": assessment["difficulty"],
                "question_count": assessment["question_count"],
                "batches": assessment.get("batches", []),
                "status": assessment["status"],
                "is_active": assessment["is_active"],
                "created_at": assessment["created_at"].isoformat(),
                "submission_count": submission_count,
                "time_limit": assessment.get("time_limit", 30),
                "description": assessment.get("description", ""),
                "type": assessment.get("type", "teacher")
            })
        
        return assessment_list
        
    except Exception as e:
        print(f"❌ [TEACHER ASSESSMENTS] Error fetching assessments: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/assessments/create", response_model=TeacherAssessmentResponse)
async def create_teacher_assessment(
    assessment_data: TeacherAssessmentCreate,
    current_user: UserModel = Depends(require_teacher_or_admin)
):
    """Create an assessment for students"""
    try:
        db = await get_db()
        
        print(f"🤖 [TEACHER ASSESSMENT] Creating {assessment_data.type} assessment: {assessment_data.title}")
        
        # Generate unique assessment ID
        assessment_id = str(ObjectId())
        
        # Validate required fields
        if not assessment_data.batches or len(assessment_data.batches) == 0:
            raise HTTPException(status_code=400, detail="At least one batch must be selected")
        
        # Handle different assessment types
        if assessment_data.type == "ai_generated":
            if not assessment_data.topic or not assessment_data.question_count:
                raise HTTPException(status_code=400, detail="Topic and question count are required for AI-generated assessments")

            from app.services.gemini_coding_service import GeminiCodingService
            gemini_service = GeminiCodingService()
            generated_questions = await gemini_service.generate_mcq_questions(
                topic=assessment_data.topic,
                difficulty=assessment_data.difficulty,
                count=assessment_data.question_count
            )
        elif assessment_data.type == "ai_coding":
            if not assessment_data.topic or not assessment_data.question_count:
                raise HTTPException(status_code=400, detail="Topic and question count are required for AI Coding assessments")

            from app.services.gemini_coding_service import GeminiCodingService
            gemini_service = GeminiCodingService()
            generated_questions = []
            for i in range(assessment_data.question_count):
                try:
                    problem = await gemini_service.generate_coding_problem(
                        topic=assessment_data.topic,
                        difficulty=assessment_data.difficulty
                    )
                    generated_questions.append(problem)
                except Exception as e:
                    print(f"[ERROR] [AI_CODING] Failed to generate coding problem {i+1}: {e}")
                    try:
                        fallback_problem = gemini_service._get_fallback_problem(assessment_data.topic, assessment_data.difficulty)
                        generated_questions.append(fallback_problem)
                        print(f"[RECOVERY] [AI_CODING] Fallback problem used for question {i+1}")
                    except Exception as e2:
                        print(f"[CRITICAL] [AI_CODING] Failed to get fallback problem: {e2}")
                        raise HTTPException(status_code=500, detail=f"Failed to generate coding problem or fallback: {e2}")
        else:
            # Use provided questions for manual assessments
            generated_questions = assessment_data.questions or []
            if len(generated_questions) == 0:
                raise HTTPException(status_code=400, detail="At least one question is required for manual assessments")
        
        # Get topic from request or use title as fallback for manual assessments
        assessment_topic = assessment_data.topic if assessment_data.topic else assessment_data.title
        
        # Store in teacher_assessments collection
        teacher_assessment = {
            "_id": ObjectId(assessment_id),
            "title": assessment_data.title,
            "topic": assessment_topic,
            "difficulty": assessment_data.difficulty,
            "question_count": assessment_data.question_count or len(generated_questions),
            "questions": generated_questions,
            "batches": assessment_data.batches or [],
            "teacher_id": str(current_user.id),  # Store as string for consistency
            "type": assessment_data.type,
            "created_at": datetime.utcnow(),
            "is_active": True,
            "status": "published"  # Set to published so students can see it
        }
        
        # Add optional fields if provided
        if assessment_data.description:
            teacher_assessment["description"] = assessment_data.description
        if assessment_data.time_limit:
            teacher_assessment["time_limit"] = assessment_data.time_limit
        
        await db.teacher_assessments.insert_one(teacher_assessment)
        
        # Store questions in ai_questions collection for review
        processed_questions = []
        for question in generated_questions:
            # For coding, mark with source and store format
            q_source = "ai_coding_generated" if assessment_data.type == "ai_coding" else ("teacher_generated" if assessment_data.type == "mcq" else "ai_generated")
            question_doc = {
                **question,
                "topic": assessment_topic,
                "difficulty": assessment_data.difficulty,
                "assessment_id": assessment_id,
                "created_at": datetime.utcnow(),
                "source": q_source
            }
            await db.ai_questions.insert_one(question_doc)
            processed_questions.append(question)
        # Update teacher_assessment with processed questions
        await db.teacher_assessments.update_one(
            {"_id": ObjectId(assessment_id)},
            {"$set": {"questions": processed_questions}}
        )
        
        # Get all students from selected batches
        student_ids = []
        batches = assessment_data.batches or []
        for batch_id in batches:
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
                "message": f"A new {assessment_data.difficulty} assessment on {assessment_topic} has been assigned to you.",
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
        import traceback
        print(f"❌ [TEACHER ASSESSMENT] Error creating assessment: {str(e)}")
        print(f"❌ [TEACHER ASSESSMENT] Traceback:")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create assessment: {str(e)}"
        )