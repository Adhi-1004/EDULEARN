"""
Enhanced Admin Dashboard API
Comprehensive platform management and oversight features
"""
from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
from pydantic import BaseModel, Field
from ..db import get_db
from ..schemas.schemas import UserCreate, UserResponse
from ..models.models import UserModel
from ..dependencies import require_admin_only, require_user_management, require_platform_management, require_analytics_access, require_content_management
import os
import csv
import io

router = APIRouter(prefix="/admin", tags=["enhanced_admin_dashboard"])
security = HTTPBearer()

# Response Models
class UserCreateResponse(BaseModel):
    id: str
    username: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    message: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    is_admin: Optional[bool] = None

# Enhanced Models
class UserAnalytics(BaseModel):
    user_id: str
    name: str
    email: str
    role: str
    last_login: Optional[datetime]
    total_logins: int
    activity_score: float
    progress_percentage: float
    assessments_taken: int
    average_score: float
    badges_earned: int
    streak_days: int

class PlatformMetrics(BaseModel):
    total_users: int
    active_users_today: int
    active_users_week: int
    active_users_month: int
    total_teachers: int
    total_students: int
    total_assessments: int
    total_questions: int
    total_batches: int
    platform_health_score: float
    user_engagement_rate: float
    content_completion_rate: float

class ContentAnalytics(BaseModel):
    content_id: str
    title: str
    type: str
    creator: str
    views: int
    completions: int
    average_score: float
    popularity_score: float
    difficulty_rating: float
    last_updated: datetime

class TeacherPerformance(BaseModel):
    teacher_id: str
    name: str
    email: str
    total_students: int
    total_batches: int
    total_assessments_created: int
    average_student_score: float
    student_satisfaction: float
    content_quality_score: float
    engagement_score: float

class BulkUserImport(BaseModel):
    users: List[Dict[str, Any]]
    success_count: int
    error_count: int
    errors: List[str]

class ContentCuration(BaseModel):
    content_id: str
    title: str
    type: str
    creator: str
    status: str  # pending, approved, rejected
    review_notes: Optional[str]
    quality_score: float
    difficulty_level: str
    subject: str
    created_at: datetime
    reviewed_at: Optional[datetime]

# User Monitoring Endpoints
@router.get("/users/analytics", response_model=List[UserAnalytics])
async def get_user_analytics(
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    role: Optional[str] = Query(None),
    sort_by: str = Query("activity_score", regex="^(activity_score|progress_percentage|average_score|last_login)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    admin: dict = Depends(require_analytics_access)
):
    """Get comprehensive user analytics with detailed metrics"""
    try:
        db = await get_db()
        
        # Build query
        query = {}
        if role:
            query["role"] = role
        
        # Get users with pagination
        users = await db.users.find(query).skip(offset).limit(limit).to_list(length=limit)
        
        analytics = []
        for user in users:
            user_id = str(user["_id"])
            
            # Calculate user metrics
            total_logins = await db.user_sessions.count_documents({"user_id": user_id})
            last_login = await db.user_sessions.find_one(
                {"user_id": user_id}, 
                sort=[("timestamp", -1)]
            )
            
            # Get assessment data
            assessment_results = await db.results.find({"user_id": user_id}).to_list(length=1000)
            assessments_taken = len(assessment_results)
            average_score = sum(r.get("score", 0) for r in assessment_results) / max(assessments_taken, 1)
            
            # Get progress data
            progress_data = await db.user_progress.find({"user_id": user_id}).to_list(length=100)
            progress_percentage = sum(p.get("completion_percentage", 0) for p in progress_data) / max(len(progress_data), 1)
            
            # Get badges and streaks
            badges_earned = await db.user_badges.count_documents({"user_id": user_id})
            streak_data = await db.user_streaks.find_one({"user_id": user_id})
            streak_days = streak_data.get("current_streak", 0) if streak_data else 0
            
            # Calculate activity score
            activity_score = min(100, (total_logins * 0.3 + assessments_taken * 0.4 + progress_percentage * 0.3))
            
            analytics.append(UserAnalytics(
                user_id=user_id,
                name=user.get("name", user.get("username", "Unknown")),
                email=user.get("email", ""),
                role=user.get("role", "student"),
                last_login=last_login.get("timestamp") if last_login else None,
                total_logins=total_logins,
                activity_score=activity_score,
                progress_percentage=progress_percentage,
                assessments_taken=assessments_taken,
                average_score=average_score,
                badges_earned=badges_earned,
                streak_days=streak_days
            ))
        
        # Sort results
        reverse = order == "desc"
        analytics.sort(key=lambda x: getattr(x, sort_by), reverse=reverse)
        
        return analytics
        
    except Exception as e:
        print(f"[ERROR] [ADMIN] Failed to get user analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve user analytics")

@router.get("/users/{user_id}/details")
async def get_user_details(
    user_id: str,
    admin: dict = Depends(require_analytics_access)
):
    """Get detailed information about a specific user"""
    try:
        db = await get_db()
        
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID")
        
        # Get user basic info
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get detailed analytics
        user_analytics = await get_user_analytics(limit=1, offset=0, admin=admin)
        analytics = user_analytics[0] if user_analytics else None
        
        # Get recent activity
        recent_activity = await db.user_activity.find(
            {"user_id": user_id}
        ).sort("timestamp", -1).limit(20).to_list(length=20)
        
        # Get assessment history
        assessment_history = await db.results.find(
            {"user_id": user_id}
        ).sort("timestamp", -1).limit(10).to_list(length=10)
        
        # Get badges and achievements
        badges = await db.user_badges.find({"user_id": user_id}).to_list(length=50)
        
        return {
            "user": {
                "id": str(user["_id"]),
                "name": user.get("name", ""),
                "email": user.get("email", ""),
                "role": user.get("role", "student"),
                "created_at": user.get("created_at"),
                "last_login": user.get("last_login"),
                "is_active": user.get("is_active", True)
            },
            "analytics": analytics.dict() if analytics else None,
            "recent_activity": recent_activity,
            "assessment_history": assessment_history,
            "badges": badges
        }
        
    except Exception as e:
        print(f"[ERROR] [ADMIN] Failed to get user details: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve user details")

# User Management Endpoints
@router.post("/users", response_model=UserCreateResponse)
async def create_user(
    user_data: UserCreate,
    admin: dict = Depends(require_user_management)
):
    """Create a new user"""
    try:
        db = await get_db()
        
        # Check if user already exists
        existing_user = await db.users.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")
        
        # Create user
        user_doc = {
            "username": user_data.username,
            "email": user_data.email,
            "password": UserModel.hash_password(user_data.password),
            "role": user_data.role,
            "is_admin": user_data.role == "admin",
            "name": user_data.name,
            "created_at": datetime.utcnow(),
            "is_active": True
        }
        
        result = await db.users.insert_one(user_doc)
        user_doc["_id"] = result.inserted_id
        
        return UserCreateResponse(
            id=str(result.inserted_id),
            username=user_doc["username"],
            email=user_doc["email"],
            role=user_doc["role"],
            message="User created successfully"
        )
        
    except Exception as e:
        print(f"[ERROR] [ADMIN] Failed to create user: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create user")

@router.put("/users/{user_id}", response_model=UserCreateResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    admin: dict = Depends(require_user_management)
):
    """Update user information"""
    try:
        db = await get_db()
        
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID")
        
        # Build update data
        update_data = {}
        if user_data.name is not None:
            update_data["name"] = user_data.name
        if user_data.email is not None:
            update_data["email"] = user_data.email
        if user_data.role is not None:
            update_data["role"] = user_data.role
            update_data["is_admin"] = user_data.role == "admin"
        if user_data.is_admin is not None:
            update_data["is_admin"] = user_data.is_admin
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        update_data["updated_at"] = datetime.utcnow()
        
        result = await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserCreateResponse(
            id=user_id,
            message="User updated successfully"
        )
        
    except Exception as e:
        print(f"[ERROR] [ADMIN] Failed to update user: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update user")

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    admin: dict = Depends(require_user_management)
):
    """Delete a user"""
    try:
        db = await get_db()
        
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID")
        
        # Check if user exists
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Soft delete - mark as inactive
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"is_active": False, "deleted_at": datetime.utcnow()}}
        )
        
        return {"message": "User deleted successfully"}
        
    except Exception as e:
        print(f"[ERROR] [ADMIN] Failed to delete user: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete user")

# Bulk User Import/Export
@router.post("/users/bulk-import", response_model=BulkUserImport)
async def bulk_import_users(
    file: UploadFile = File(...),
    admin: dict = Depends(require_user_management)
):
    """Import users from CSV file"""
    try:
        db = await get_db()
        
        # Read CSV file
        content = await file.read()
        csv_content = content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        
        users = []
        success_count = 0
        error_count = 0
        errors = []
        
        for row in csv_reader:
            try:
                # Validate required fields
                if not row.get('email') or not row.get('name'):
                    errors.append(f"Row {len(users) + 1}: Missing required fields")
                    error_count += 1
                    continue
                
                # Check if user already exists
                existing_user = await db.users.find_one({"email": row['email']})
                if existing_user:
                    errors.append(f"Row {len(users) + 1}: User with email {row['email']} already exists")
                    error_count += 1
                    continue
                
                # Create user data
                user_data = {
                    "name": row['name'],
                    "email": row['email'],
                    "username": row.get('username', row['email'].split('@')[0]),
                    "role": row.get('role', 'student'),
                    "password": UserModel.hash_password(row.get('password', 'defaultpassword123')),
                    "is_admin": row.get('role', 'student') == 'admin',
                    "created_at": datetime.utcnow(),
                    "is_active": True
                }
                
                users.append(user_data)
                success_count += 1
                
            except Exception as e:
                errors.append(f"Row {len(users) + 1}: {str(e)}")
                error_count += 1
        
        # Insert users
        if users:
            await db.users.insert_many(users)
        
        return BulkUserImport(
            users=[{"name": u["name"], "email": u["email"], "role": u["role"]} for u in users],
            success_count=success_count,
            error_count=error_count,
            errors=errors
        )
        
    except Exception as e:
        print(f"[ERROR] [ADMIN] Failed to bulk import users: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to import users")

@router.get("/users/export")
async def export_users(
    format: str = Query("csv", regex="^(csv|json)$"),
    role: Optional[str] = Query(None),
    admin: dict = Depends(require_analytics_access)
):
    """Export users to CSV or JSON"""
    try:
        db = await get_db()
        
        # Build query
        query = {"is_active": True}
        if role:
            query["role"] = role
        
        users = await db.users.find(query).to_list(length=10000)
        
        if format == "csv":
            # Create CSV content
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["name", "email", "username", "role", "created_at"])
            
            for user in users:
                writer.writerow([
                    user.get("name", ""),
                    user.get("email", ""),
                    user.get("username", ""),
                    user.get("role", ""),
                    user.get("created_at", "").isoformat() if user.get("created_at") else ""
                ])
            
            return {"content": output.getvalue(), "content_type": "text/csv"}
        
        else:  # JSON
            return {
                "users": [
                    {
                        "id": str(user["_id"]),
                        "name": user.get("name", ""),
                        "email": user.get("email", ""),
                        "username": user.get("username", ""),
                        "role": user.get("role", ""),
                        "created_at": user.get("created_at", "").isoformat() if user.get("created_at") else ""
                    }
                    for user in users
                ]
            }
        
    except Exception as e:
        print(f"[ERROR] [ADMIN] Failed to export users: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to export users")

# System Analytics Endpoints
@router.get("/analytics/platform", response_model=PlatformMetrics)
async def get_platform_metrics(
    admin: dict = Depends(require_analytics_access)
):
    """Get comprehensive platform metrics"""
    try:
        db = await get_db()
        
        # Basic counts
        total_users = await db.users.count_documents({"is_active": True})
        total_teachers = await db.users.count_documents({"role": "teacher", "is_active": True})
        total_students = await db.users.count_documents({"role": "student", "is_active": True})
        total_assessments = await db.assessments.count_documents({})
        total_questions = await db.questions.count_documents({})
        total_batches = await db.batches.count_documents({})
        
        # Activity metrics
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        active_users_today = await db.user_activity.count_documents({
            "timestamp": {"$gte": today}
        })
        active_users_week = await db.user_activity.count_documents({
            "timestamp": {"$gte": week_ago}
        })
        active_users_month = await db.user_activity.count_documents({
            "timestamp": {"$gte": month_ago}
        })
        
        # Calculate engagement metrics
        user_engagement_rate = (active_users_week / max(total_users, 1)) * 100
        
        # Content completion rate
        total_completions = await db.results.count_documents({})
        content_completion_rate = (total_completions / max(total_assessments * total_students, 1)) * 100
        
        # Platform health score
        platform_health_score = min(100, (
            user_engagement_rate * 0.4 +
            content_completion_rate * 0.3 +
            (active_users_today / max(total_users, 1)) * 100 * 0.3
        ))
        
        return PlatformMetrics(
            total_users=total_users,
            active_users_today=active_users_today,
            active_users_week=active_users_week,
            active_users_month=active_users_month,
            total_teachers=total_teachers,
            total_students=total_students,
            total_assessments=total_assessments,
            total_questions=total_questions,
            total_batches=total_batches,
            platform_health_score=platform_health_score,
            user_engagement_rate=user_engagement_rate,
            content_completion_rate=content_completion_rate
        )
        
    except Exception as e:
        print(f"[ERROR] [ADMIN] Failed to get platform metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve platform metrics")

@router.get("/analytics/content", response_model=List[ContentAnalytics])
async def get_content_analytics(
    limit: int = Query(50, ge=1, le=1000),
    sort_by: str = Query("popularity_score", regex="^(popularity_score|views|completions|average_score)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    admin: dict = Depends(require_analytics_access)
):
    """Get content popularity and performance analytics"""
    try:
        db = await get_db()
        
        # Get assessments with analytics
        assessments = await db.assessments.find({}).limit(limit).to_list(length=limit)
        
        analytics = []
        for assessment in assessments:
            assessment_id = str(assessment["_id"])
            
            # Get views and completions
            views = await db.assessment_views.count_documents({"assessment_id": assessment_id})
            completions = await db.results.count_documents({"assessment_id": assessment_id})
            
            # Get average score
            results = await db.results.find({"assessment_id": assessment_id}).to_list(length=1000)
            average_score = sum(r.get("score", 0) for r in results) / max(len(results), 1)
            
            # Calculate popularity score
            popularity_score = (views * 0.3 + completions * 0.7) / max(views + completions, 1) * 100
            
            analytics.append(ContentAnalytics(
                content_id=assessment_id,
                title=assessment.get("title", "Untitled"),
                type="assessment",
                creator=assessment.get("created_by", "Unknown"),
                views=views,
                completions=completions,
                average_score=average_score,
                popularity_score=popularity_score,
                difficulty_rating=assessment.get("difficulty", 0),
                last_updated=assessment.get("updated_at", assessment.get("created_at", datetime.utcnow()))
            ))
        
        # Sort results
        reverse = order == "desc"
        analytics.sort(key=lambda x: getattr(x, sort_by), reverse=reverse)
        
        return analytics
        
    except Exception as e:
        print(f"[ERROR] [ADMIN] Failed to get content analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve content analytics")

@router.get("/analytics/teachers", response_model=List[TeacherPerformance])
async def get_teacher_performance(
    limit: int = Query(50, ge=1, le=1000),
    sort_by: str = Query("average_student_score", regex="^(average_student_score|student_satisfaction|content_quality_score|engagement_score)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    admin: dict = Depends(require_analytics_access)
):
    """Get teacher performance analytics"""
    try:
        db = await get_db()
        
        # Get all teachers
        teachers = await db.users.find({"role": "teacher", "is_active": True}).limit(limit).to_list(length=limit)
        
        performance = []
        for teacher in teachers:
            teacher_id = str(teacher["_id"])
            
            # Get teacher's batches and students
            batches = await db.batches.find({"teacher_id": teacher_id}).to_list(length=100)
            total_batches = len(batches)
            total_students = sum(len(batch.get("student_ids", [])) for batch in batches)
            
            # Get assessments created by teacher
            total_assessments_created = await db.assessments.count_documents({"created_by": teacher_id})
            
            # Get student performance in teacher's batches
            batch_ids = [str(batch["_id"]) for batch in batches]
            student_results = await db.results.find({
                "batch_id": {"$in": batch_ids}
            }).to_list(length=1000)
            
            average_student_score = sum(r.get("score", 0) for r in student_results) / max(len(student_results), 1)
            
            # Calculate other metrics
            student_satisfaction = min(100, average_student_score + 20)  # Simplified calculation
            content_quality_score = min(100, (total_assessments_created * 10) + 50)  # Simplified calculation
            engagement_score = min(100, (total_students * 2) + (total_batches * 5))  # Simplified calculation
            
            performance.append(TeacherPerformance(
                teacher_id=teacher_id,
                name=teacher.get("name", teacher.get("username", "Unknown")),
                email=teacher.get("email", ""),
                total_students=total_students,
                total_batches=total_batches,
                total_assessments_created=total_assessments_created,
                average_student_score=average_student_score,
                student_satisfaction=student_satisfaction,
                content_quality_score=content_quality_score,
                engagement_score=engagement_score
            ))
        
        # Sort results
        reverse = order == "desc"
        performance.sort(key=lambda x: getattr(x, sort_by), reverse=reverse)
        
        return performance
        
    except Exception as e:
        print(f"[ERROR] [ADMIN] Failed to get teacher performance: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve teacher performance")

# Content Oversight Endpoints
@router.get("/content/library")
async def get_content_library(
    limit: int = Query(50, ge=1, le=1000),
    content_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    admin: dict = Depends(require_content_management)
):
    """Get global content library"""
    try:
        db = await get_db()
        
        # Build query
        query = {}
        if content_type:
            query["type"] = content_type
        if status:
            query["status"] = status
        
        # Get content
        content = await db.content_library.find(query).limit(limit).to_list(length=limit)
        
        return {
            "content": [
                {
                    "id": str(item["_id"]),
                    "title": item.get("title", ""),
                    "type": item.get("type", ""),
                    "subject": item.get("subject", ""),
                    "difficulty": item.get("difficulty", ""),
                    "creator": item.get("creator", ""),
                    "status": item.get("status", "pending"),
                    "created_at": item.get("created_at", ""),
                    "views": item.get("views", 0),
                    "downloads": item.get("downloads", 0)
                }
                for item in content
            ],
            "total": len(content)
        }
        
    except Exception as e:
        print(f"[ERROR] [ADMIN] Failed to get content library: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve content library")

@router.get("/content/curation", response_model=List[ContentCuration])
async def get_content_curation(
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=1000),
    admin: dict = Depends(require_content_management)
):
    """Get content for curation review"""
    try:
        db = await get_db()
        
        # Build query
        query = {}
        if status:
            query["status"] = status
        
        # Get content pending review
        content = await db.content_curation.find(query).limit(limit).to_list(length=limit)
        
        curation = []
        for item in content:
            curation.append(ContentCuration(
                content_id=str(item["_id"]),
                title=item.get("title", ""),
                type=item.get("type", ""),
                creator=item.get("creator", ""),
                status=item.get("status", "pending"),
                review_notes=item.get("review_notes"),
                quality_score=item.get("quality_score", 0),
                difficulty_level=item.get("difficulty_level", ""),
                subject=item.get("subject", ""),
                created_at=item.get("created_at", datetime.utcnow()),
                reviewed_at=item.get("reviewed_at")
            ))
        
        return curation
        
    except Exception as e:
        print(f"[ERROR] [ADMIN] Failed to get content curation: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve content curation")

@router.post("/content/{content_id}/approve")
async def approve_content(
    content_id: str,
    review_notes: Optional[str] = None,
    admin: dict = Depends(require_content_management)
):
    """Approve content for publication"""
    try:
        db = await get_db()
        
        if not ObjectId.is_valid(content_id):
            raise HTTPException(status_code=400, detail="Invalid content ID")
        
        # Update content status
        result = await db.content_curation.update_one(
            {"_id": ObjectId(content_id)},
            {
                "$set": {
                    "status": "approved",
                    "review_notes": review_notes,
                    "reviewed_at": datetime.utcnow(),
                    "reviewed_by": str(admin["_id"])
                }
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Content not found")
        
        return {"message": "Content approved successfully"}
        
    except Exception as e:
        print(f"[ERROR] [ADMIN] Failed to approve content: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to approve content")

@router.post("/content/{content_id}/reject")
async def reject_content(
    content_id: str,
    review_notes: str,
    admin: dict = Depends(require_content_management)
):
    """Reject content"""
    try:
        db = await get_db()
        
        if not ObjectId.is_valid(content_id):
            raise HTTPException(status_code=400, detail="Invalid content ID")
        
        # Update content status
        result = await db.content_curation.update_one(
            {"_id": ObjectId(content_id)},
            {
                "$set": {
                    "status": "rejected",
                    "review_notes": review_notes,
                    "reviewed_at": datetime.utcnow(),
                    "reviewed_by": str(admin["_id"])
                }
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Content not found")
        
        return {"message": "Content rejected successfully"}
        
    except Exception as e:
        print(f"[ERROR] [ADMIN] Failed to reject content: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to reject content")