from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel
from ..db import get_db
from ..schemas import UserResponse
from ..models import UserModel
import os

router = APIRouter(prefix="/teacher", tags=["teacher_dashboard"])
security = HTTPBearer()

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token - teacher role required"""
    try:
        from jose import jwt
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        db = await get_db()
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        # Check if user is a teacher
        user_role = user.get("role", "student")
        if user_role != "teacher":
            raise HTTPException(status_code=403, detail="Access denied. Teacher role required.")
        
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

# Student Management Models
class StudentResponse(BaseModel):
    id: str
    email: str
    username: Optional[str] = None
    name: Optional[str] = None
    profile_picture: Optional[str] = None
    is_admin: bool = False
    role: str = "student"
    progress: Optional[float] = None
    last_active: Optional[str] = None
    batch: Optional[str] = None

class BatchCreate(BaseModel):
    name: str
    description: Optional[str] = None

class BatchResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    student_count: int
    created_at: str
    teacher_id: str

class BatchStudentResponse(BaseModel):
    batch_id: str
    student_id: str
    added_at: str

class AddStudentToBatchRequest(BaseModel):
    student_email: Optional[str] = None
    student_name: Optional[str] = None
    student_id: Optional[str] = None

class AddStudentToBatchResponse(BaseModel):
    success: bool
    message: str
    student_id: Optional[str] = None
    student_name: Optional[str] = None

# Assessment Models
class AssessmentCreate(BaseModel):
    title: str
    topic: str
    difficulty: str
    question_count: int
    description: Optional[str] = None
    assigned_to: Optional[List[str]] = None  # batch IDs or student IDs

class AssessmentResponse(BaseModel):
    id: str
    title: str
    topic: str
    difficulty: str
    question_count: int
    description: Optional[str] = None
    created_by: str
    created_at: str
    assigned_to: Optional[List[str]] = None

# Analytics Models
class StudentProgress(BaseModel):
    student_id: str
    student_name: str
    average_score: float
    completed_assessments: int
    last_active: str

class ClassAnalytics(BaseModel):
    total_students: int
    average_class_score: float
    assessment_completion_rate: float
    active_students: int
    recent_activities: List[Dict[str, Any]]

# Teacher Dashboard Endpoints

@router.get("/students", response_model=List[StudentResponse])
async def get_teacher_students(teacher: dict = Depends(get_current_user)):
    """Get all students assigned to this teacher"""
    try:
        db = await get_db()
        
        # In a real implementation, this would filter students by teacher assignment
        # For now, we'll return all students
        students_cursor = await db.users.find({"role": "student"}).to_list(None)
        students = []
        
        for student in students_cursor:
            # Get student progress data (mock implementation)
            progress_data = await get_student_progress(db, str(student["_id"]))
            
            student_response = StudentResponse(
                id=str(student["_id"]),
                email=student["email"],
                username=student.get("username"),
                name=student.get("name"),
                profile_picture=student.get("profile_picture"),
                is_admin=student.get("is_admin", False),
                role=student.get("role", "student"),
                progress=progress_data.get("average_score", 0),
                last_active=progress_data.get("last_active", ""),
                batch=progress_data.get("batch")
            )
            students.append(student_response)
        
        return students
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/students/{student_id}", response_model=StudentResponse)
async def get_student_details(student_id: str, teacher: dict = Depends(get_current_user)):
    """Get detailed information for a specific student"""
    try:
        db = await get_db()
        
        if not ObjectId.is_valid(student_id):
            raise HTTPException(status_code=400, detail="Invalid student ID")
        
        student = await db.users.find_one({"_id": ObjectId(student_id), "role": "student"})
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Get student progress data
        progress_data = await get_student_progress(db, student_id)
        
        return StudentResponse(
            id=str(student["_id"]),
            email=student["email"],
            username=student.get("username"),
            name=student.get("name"),
            profile_picture=student.get("profile_picture"),
            is_admin=student.get("is_admin", False),
            role=student.get("role", "student"),
            progress=progress_data.get("average_score", 0),
            last_active=progress_data.get("last_active", ""),
            batch=progress_data.get("batch")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Batch Management Endpoints

@router.post("/batches", response_model=BatchResponse)
async def create_batch(batch_data: BatchCreate, teacher: dict = Depends(get_current_user)):
    """Create a new batch"""
    try:
        db = await get_db()
        
        batch_doc = {
            "name": batch_data.name,
            "description": batch_data.description,
            "teacher_id": str(teacher["_id"]),
            "created_at": datetime.utcnow(),
            "student_ids": []
        }
        
        result = await db.batches.insert_one(batch_doc)
        
        return BatchResponse(
            id=str(result.inserted_id),
            name=batch_data.name,
            description=batch_data.description,
            student_count=0,
            created_at=batch_doc["created_at"].isoformat(),
            teacher_id=str(teacher["_id"])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/batches", response_model=List[BatchResponse])
async def get_teacher_batches(teacher: dict = Depends(get_current_user)):
    """Get all batches created by this teacher"""
    try:
        db = await get_db()
        
        batches_cursor = await db.batches.find({"teacher_id": str(teacher["_id"])}).to_list(None)
        batches = []
        
        for batch in batches_cursor:
            # Count students in batch
            student_count = len(batch.get("student_ids", []))
            
            batch_response = BatchResponse(
                id=str(batch["_id"]),
                name=batch["name"],
                description=batch.get("description"),
                student_count=student_count,
                created_at=batch["created_at"].isoformat(),
                teacher_id=batch["teacher_id"]
            )
            batches.append(batch_response)
        
        return batches
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/batches/{batch_id}", response_model=BatchResponse)
async def get_batch_details(batch_id: str, teacher: dict = Depends(get_current_user)):
    """Get detailed information for a specific batch"""
    try:
        db = await get_db()
        
        if not ObjectId.is_valid(batch_id):
            raise HTTPException(status_code=400, detail="Invalid batch ID")
        
        batch = await db.batches.find_one({"_id": ObjectId(batch_id), "teacher_id": str(teacher["_id"])})
        if not batch:
            raise HTTPException(status_code=404, detail="Batch not found")
        
        # Count students in batch
        student_count = len(batch.get("student_ids", []))
        
        return BatchResponse(
            id=str(batch["_id"]),
            name=batch["name"],
            description=batch.get("description"),
            student_count=student_count,
            created_at=batch["created_at"].isoformat(),
            teacher_id=batch["teacher_id"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batches/{batch_id}/students/{student_id}", response_model=BatchStudentResponse)
async def add_student_to_batch(batch_id: str, student_id: str, teacher: dict = Depends(get_current_user)):
    """Add a student to a batch"""
    try:
        db = await get_db()
        
        if not ObjectId.is_valid(batch_id) or not ObjectId.is_valid(student_id):
            raise HTTPException(status_code=400, detail="Invalid ID")
        
        # Check if batch exists and belongs to teacher
        batch = await db.batches.find_one({"_id": ObjectId(batch_id), "teacher_id": str(teacher["_id"])})
        if not batch:
            raise HTTPException(status_code=404, detail="Batch not found")
        
        # Check if student exists
        student = await db.users.find_one({"_id": ObjectId(student_id), "role": "student"})
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Add student to batch if not already added
        if student_id not in batch.get("student_ids", []):
            await db.batches.update_one(
                {"_id": ObjectId(batch_id)},
                {"$addToSet": {"student_ids": student_id}}
            )
        
        return BatchStudentResponse(
            batch_id=batch_id,
            student_id=student_id,
            added_at=datetime.utcnow().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batches/{batch_id}/students/add", response_model=AddStudentToBatchResponse)
async def add_student_to_batch_by_email_or_name(
    batch_id: str, 
    request: AddStudentToBatchRequest, 
    teacher: dict = Depends(get_current_user)
):
    """Add a student to a batch by email, name, or student ID"""
    try:
        db = await get_db()
        
        if not ObjectId.is_valid(batch_id):
            raise HTTPException(status_code=400, detail="Invalid batch ID")
        
        # Check if batch exists and belongs to teacher
        batch = await db.batches.find_one({"_id": ObjectId(batch_id), "teacher_id": str(teacher["_id"])})
        if not batch:
            raise HTTPException(status_code=404, detail="Batch not found")
        
        # Find student by email, name, or ID
        student = None
        student_query = {"role": "student"}
        
        if request.student_id and ObjectId.is_valid(request.student_id):
            student = await db.users.find_one({"_id": ObjectId(request.student_id), "role": "student"})
        elif request.student_email:
            student = await db.users.find_one({"email": request.student_email, "role": "student"})
        elif request.student_name:
            # Search by name (case insensitive)
            student = await db.users.find_one({
                "name": {"$regex": request.student_name, "$options": "i"}, 
                "role": "student"
            })
        
        if not student:
            return AddStudentToBatchResponse(
                success=False,
                message="Student not found. Please check the email, name, or ID and try again."
            )
        
        student_id = str(student["_id"])
        student_name = student.get("name") or student.get("username") or student.get("email")
        
        # Check if student is already in the batch
        if student_id in batch.get("student_ids", []):
            return AddStudentToBatchResponse(
                success=False,
                message=f"Student {student_name} is already in this batch."
            )
        
        # Add student to batch
        await db.batches.update_one(
            {"_id": ObjectId(batch_id)},
            {"$addToSet": {"student_ids": student_id}}
        )
        
        return AddStudentToBatchResponse(
            success=True,
            message=f"Student {student_name} has been successfully added to the batch.",
            student_id=student_id,
            student_name=student_name
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/batches/{batch_id}/students/{student_id}")
async def remove_student_from_batch(batch_id: str, student_id: str, teacher: dict = Depends(get_current_user)):
    """Remove a student from a batch"""
    try:
        db = await get_db()
        
        if not ObjectId.is_valid(batch_id) or not ObjectId.is_valid(student_id):
            raise HTTPException(status_code=400, detail="Invalid ID")
        
        # Check if batch exists and belongs to teacher
        batch = await db.batches.find_one({"_id": ObjectId(batch_id), "teacher_id": str(teacher["_id"])})
        if not batch:
            raise HTTPException(status_code=404, detail="Batch not found")
        
        # Remove student from batch
        await db.batches.update_one(
            {"_id": ObjectId(batch_id)},
            {"$pull": {"student_ids": student_id}}
        )
        
        return {"success": True, "message": "Student removed from batch"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Assessment Management Endpoints

@router.post("/assessments", response_model=AssessmentResponse)
async def create_assessment(assessment_data: AssessmentCreate, teacher: dict = Depends(get_current_user)):
    """Create a new assessment"""
    try:
        db = await get_db()
        
        assessment_doc = {
            "title": assessment_data.title,
            "topic": assessment_data.topic,
            "difficulty": assessment_data.difficulty,
            "question_count": assessment_data.question_count,
            "description": assessment_data.description,
            "created_by": str(teacher["_id"]),
            "created_at": datetime.utcnow(),
            "assigned_to": assessment_data.assigned_to or []
        }
        
        result = await db.assessments.insert_one(assessment_doc)
        
        return AssessmentResponse(
            id=str(result.inserted_id),
            title=assessment_data.title,
            topic=assessment_data.topic,
            difficulty=assessment_data.difficulty,
            question_count=assessment_data.question_count,
            description=assessment_data.description,
            created_by=str(teacher["_id"]),
            created_at=assessment_doc["created_at"].isoformat(),
            assigned_to=assessment_data.assigned_to or []
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/assessments", response_model=List[AssessmentResponse])
async def get_teacher_assessments(teacher: dict = Depends(get_current_user)):
    """Get all assessments created by this teacher"""
    try:
        db = await get_db()
        
        assessments_cursor = await db.assessments.find({"created_by": str(teacher["_id"])}).to_list(None)
        assessments = []
        
        for assessment in assessments_cursor:
            assessment_response = AssessmentResponse(
                id=str(assessment["_id"]),
                title=assessment["title"],
                topic=assessment["topic"],
                difficulty=assessment["difficulty"],
                question_count=assessment["question_count"],
                description=assessment.get("description"),
                created_by=assessment["created_by"],
                created_at=assessment["created_at"].isoformat(),
                assigned_to=assessment.get("assigned_to", [])
            )
            assessments.append(assessment_response)
        
        return assessments
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Analytics Endpoints

@router.get("/analytics/class", response_model=ClassAnalytics)
async def get_class_analytics(teacher: dict = Depends(get_current_user)):
    """Get class-level analytics"""
    try:
        db = await get_db()
        
        # Get all students assigned to teacher (mock implementation)
        students_cursor = await db.users.find({"role": "student"}).to_list(None)
        student_ids = [str(student["_id"]) for student in students_cursor]
        
        # Get assessment results for these students
        results_cursor = await db.results.find({"user_id": {"$in": student_ids}}).to_list(None)
        
        total_students = len(student_ids)
        total_assessments = len(results_cursor)
        
        # Calculate average class score
        if results_cursor:
            total_score = sum(result["score"] for result in results_cursor)
            total_questions = sum(result["total_questions"] for result in results_cursor)
            average_class_score = (total_score / total_questions) * 100 if total_questions > 0 else 0
        else:
            average_class_score = 0
        
        # Calculate completion rate
        assessment_completion_rate = (total_assessments / (total_students * 2)) * 100 if total_students > 0 else 0
        
        # Count active students (those with recent results)
        active_students = len(set(result["user_id"] for result in results_cursor))
        
        # Get recent activities (mock)
        recent_activities = []
        for result in results_cursor[-5:]:  # Last 5 results
            student = await db.users.find_one({"_id": ObjectId(result["user_id"])})
            recent_activities.append({
                "student_name": student.get("name", "Unknown") if student else "Unknown",
                "topic": result["topic"],
                "score": result["score"],
                "total_questions": result["total_questions"],
                "date": result["date"].isoformat() if isinstance(result["date"], datetime) else str(result["date"])
            })
        
        return ClassAnalytics(
            total_students=total_students,
            average_class_score=average_class_score,
            assessment_completion_rate=assessment_completion_rate,
            active_students=active_students,
            recent_activities=recent_activities
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/students", response_model=List[StudentProgress])
async def get_student_progress_list(teacher: dict = Depends(get_current_user)):
    """Get progress data for all students"""
    try:
        db = await get_db()
        
        # Get all students
        students_cursor = await db.users.find({"role": "student"}).to_list(None)
        progress_list = []
        
        for student in students_cursor:
            # Get student progress data
            progress_data = await get_student_progress(db, str(student["_id"]))
            
            student_progress = StudentProgress(
                student_id=str(student["_id"]),
                student_name=student.get("name", "Unknown"),
                average_score=progress_data.get("average_score", 0),
                completed_assessments=progress_data.get("completed_assessments", 0),
                last_active=progress_data.get("last_active", "")
            )
            progress_list.append(student_progress)
        
        # Sort by average score (descending)
        progress_list.sort(key=lambda x: x.average_score, reverse=True)
        
        return progress_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Helper Functions

async def get_student_progress(db, student_id: str) -> Dict[str, Any]:
    """Get progress data for a student"""
    try:
        # Get assessment results for student
        results_cursor = await db.results.find({"user_id": student_id}).to_list(None)
        
        if not results_cursor:
            return {
                "average_score": 0,
                "completed_assessments": 0,
                "last_active": "",
                "batch": None
            }
        
        # Calculate average score
        total_score = sum(result["score"] for result in results_cursor)
        total_questions = sum(result["total_questions"] for result in results_cursor)
        average_score = (total_score / total_questions) * 100 if total_questions > 0 else 0
        
        # Get last active date
        last_result = max(results_cursor, key=lambda x: x["date"])
        last_active = last_result["date"].isoformat() if isinstance(last_result["date"], datetime) else str(last_result["date"])
        
        # Get batch information (mock)
        batch = None
        batch_doc = await db.batches.find_one({"student_ids": student_id})
        if batch_doc:
            batch = batch_doc["name"]
        
        return {
            "average_score": round(average_score, 2),
            "completed_assessments": len(results_cursor),
            "last_active": last_active,
            "batch": batch
        }
    except Exception as e:
        return {
            "average_score": 0,
            "completed_assessments": 0,
            "last_active": "",
            "batch": None
        }

# Add missing imports at the top
from pydantic import BaseModel