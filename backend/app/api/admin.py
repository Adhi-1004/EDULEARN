"""
Admin endpoints
Handles admin-specific functionality, user management, and platform administration
"""
from fastapi import APIRouter, HTTPException, Depends, status, Query, UploadFile, File
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
import csv
import io

from ..core.security import security_manager
from ..db import get_db
from ..schemas.schemas import UserCreate, UserResponse, UserUpdate
from ..models.models import UserModel
from ..dependencies import require_admin, require_user_management, require_platform_management

router = APIRouter()

# Response Models
class PlatformStatsResponse(BaseModel):
    total_users: int
    active_users_today: int
    active_users_week: int
    total_teachers: int
    total_students: int
    total_assessments: int
    platform_health_score: int
    user_engagement_rate: float
    pending_reviews: int
    system_alerts: int

class UserActivityResponse(BaseModel):
    user_id: str
    username: str
    last_login: Optional[datetime]
    activity_score: float
    recent_actions: List[Dict[str, Any]]

class SystemHealthResponse(BaseModel):
    database_status: str
    api_status: str
    services_status: Dict[str, str]
    uptime: str
    version: str

@router.get("/analytics/platform", response_model=PlatformStatsResponse)
@router.get("/stats/platform", response_model=PlatformStatsResponse)
async def get_platform_stats(current_user: UserModel = Depends(require_admin)):
    """Get comprehensive platform statistics"""
    try:
        db = await get_db()
        
        # Get user counts by role
        total_users = await db.users.count_documents({})
        total_teachers = await db.users.count_documents({"role": "teacher"})
        total_students = await db.users.count_documents({"role": "student"})
        
        # Get active users (today and this week)
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = today - timedelta(days=7)
        
        active_users_today = await db.users.count_documents({
            "last_login": {"$gte": today}
        })
        active_users_week = await db.users.count_documents({
            "last_login": {"$gte": week_ago}
        })
        
        # Get content counts (placeholders for now)
        total_assessments = await db.assessments.count_documents({}) if hasattr(db, 'assessments') else 0
        
        # Calculate platform health score (0-100)
        health_score = 0
        if total_users > 0:
            health_score += 20
        if active_users_today > 0:
            health_score += 30
        if total_teachers > 0:
            health_score += 25
        if total_students > 0:
            health_score += 25
        
        # Calculate user engagement rate
        engagement_rate = (active_users_week / total_users * 100) if total_users > 0 else 0
        
        # Mock data for pending reviews and system alerts
        pending_reviews = 3  # Placeholder
        system_alerts = 1    # Placeholder
        
        return PlatformStatsResponse(
            total_users=total_users,
            active_users_today=active_users_today,
            active_users_week=active_users_week,
            total_teachers=total_teachers,
            total_students=total_students,
            total_assessments=total_assessments,
            platform_health_score=health_score,
            user_engagement_rate=engagement_rate,
            pending_reviews=pending_reviews,
            system_alerts=system_alerts
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get platform stats: {str(e)}"
        )

@router.get("/users/activity", response_model=List[UserActivityResponse])
async def get_user_activity(
    limit: int = Query(50, ge=1, le=100),
    current_user: UserModel = Depends(require_admin)
):
    """Get user activity overview"""
    try:
        db = await get_db()
        
        # Get recent user activity
        pipeline = [
            {"$match": {"last_login": {"$exists": True, "$ne": None}}},
            {"$sort": {"last_login": -1}},
            {"$limit": limit},
            {"$project": {
                "user_id": {"$toString": "$_id"},
                "username": 1,
                "last_login": 1,
                "role": 1
            }}
        ]
        
        activities = []
        async for doc in db.users.aggregate(pipeline):
            # Calculate activity score (placeholder logic)
            activity_score = 0.8 if doc.get("last_login") else 0.0
            
            activities.append(UserActivityResponse(
                user_id=doc["user_id"],
                username=doc["username"],
                last_login=doc.get("last_login"),
                activity_score=activity_score,
                recent_actions=[]  # Placeholder
            ))
        
        return activities
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user activity: {str(e)}"
        )

@router.get("/system/health", response_model=SystemHealthResponse)
async def get_system_health(current_user: UserModel = Depends(require_admin)):
    """Get system health status"""
    try:
        db = await get_db()
        
        # Test database connection
        try:
            await db.command("ping")
            database_status = "healthy"
        except:
            database_status = "unhealthy"
        
        # Check API status
        api_status = "healthy"
        
        # Check services status
        services_status = {
            "database": database_status,
            "api": api_status,
            "authentication": "healthy",
            "file_storage": "healthy"
        }
        
        return SystemHealthResponse(
            database_status=database_status,
            api_status=api_status,
            services_status=services_status,
            uptime="24h",  # Placeholder
            version="1.0.0"  # Placeholder
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system health: {str(e)}"
        )

@router.post("/users/bulk-import")
async def bulk_import_users(
    file: UploadFile = File(...),
    current_user: UserModel = Depends(require_user_management)
):
    """Bulk import users from CSV file"""
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be a CSV"
            )
        
        content = await file.read()
        csv_content = content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        
        db = await get_db()
        imported_count = 0
        errors = []
        
        for row in csv_reader:
            try:
                # Validate required fields
                if not all(field in row for field in ['username', 'email', 'role']):
                    errors.append(f"Missing required fields in row: {row}")
                    continue
                
                # Check if user already exists
                existing_user = await db.users.find_one({"email": row['email']})
                if existing_user:
                    errors.append(f"User with email {row['email']} already exists")
                    continue
                
                # Create user document
                user_doc = {
                    "username": row['username'],
                    "email": row['email'],
                    "role": row['role'],
                    "password": "default_password",  # Should be hashed
                    "created_at": datetime.utcnow(),
                    "is_active": True
                }
                
                await db.users.insert_one(user_doc)
                imported_count += 1
                
            except Exception as e:
                errors.append(f"Error processing row {row}: {str(e)}")
        
        return {
            "message": f"Bulk import completed",
            "imported_count": imported_count,
            "errors": errors
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk import failed: {str(e)}"
        )

@router.get("/users/export")
async def export_users(
    format: str = Query("csv", regex="^(csv|json)$"),
    current_user: UserModel = Depends(require_user_management)
):
    """Export users data"""
    try:
        db = await get_db()
        
        # Get all users
        users_cursor = db.users.find({}, {"password": 0})
        users = []
        async for user_doc in users_cursor:
            users.append(user_doc)
        
        if format == "csv":
            # Generate CSV content
            if not users:
                csv_content = "username,email,role,created_at\n"
            else:
                csv_content = "username,email,role,created_at\n"
                for user in users:
                    csv_content += f"{user.get('username', '')},{user.get('email', '')},{user.get('role', '')},{user.get('created_at', '')}\n"
            
            return {
                "content": csv_content,
                "filename": f"users_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv",
                "content_type": "text/csv"
            }
        
        elif format == "json":
            return {
                "content": users,
                "filename": f"users_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json",
                "content_type": "application/json"
            }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export failed: {str(e)}"
        )

@router.post("/users/{user_id}/reset-password")
async def reset_user_password(
    user_id: str,
    current_user: UserModel = Depends(require_user_management)
):
    """Reset user password (Admin only)"""
    try:
        db = await get_db()
        
        # Check if user exists
        user_doc = await db.users.find_one({"_id": user_id})
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Generate temporary password (in real app, send via email)
        temp_password = "temp_password_123"  # Should be generated securely
        
        # Update password (should be hashed)
        await db.users.update_one(
            {"_id": user_id},
            {"$set": {"password": temp_password, "updated_at": datetime.utcnow()}}
        )
        
        return {
            "message": "Password reset successfully",
            "temporary_password": temp_password  # Remove in production
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Password reset failed: {str(e)}"
        )

# Additional admin endpoints for dashboard features
@router.get("/users")
async def get_all_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    role: Optional[str] = Query(None),
    current_user: UserModel = Depends(require_admin)
):
    """Get all users with pagination and filtering"""
    try:
        db = await get_db()
        
        # Build filter
        filter_dict = {}
        if role:
            filter_dict["role"] = role
        
        # Get total count
        total_users = await db.users.count_documents(filter_dict)
        
        # Get users with pagination
        skip = (page - 1) * limit
        users_cursor = db.users.find(filter_dict, {"password": 0}).skip(skip).limit(limit)
        users = await users_cursor.to_list(length=limit)
        
        # Format user data
        user_list = []
        for user in users:
            user_list.append({
                "id": str(user["_id"]),
                "username": user.get("username", ""),
                "email": user.get("email", ""),
                "role": user.get("role", ""),
                "is_active": user.get("is_active", True),
                "created_at": user.get("created_at", ""),
                "last_login": user.get("last_login", "")
            })
        
        return {
            "users": user_list,
            "total": total_users,
            "page": page,
            "limit": limit,
            "total_pages": (total_users + limit - 1) // limit
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get users: {str(e)}"
        )

@router.get("/analytics/overview")
async def get_analytics_overview(current_user: UserModel = Depends(require_admin)):
    """Get analytics overview for admin dashboard"""
    try:
        db = await get_db()
        
        # Get user growth data (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        user_growth = await db.users.count_documents({
            "created_at": {"$gte": thirty_days_ago}
        })
        
        # Get assessment completion data
        total_completions = await db.results.count_documents({}) if hasattr(db, 'results') else 0
        
        # Get system performance metrics
        system_metrics = {
            "avg_response_time": "120ms",  # Placeholder
            "uptime_percentage": 99.9,     # Placeholder
            "error_rate": 0.1,             # Placeholder
            "active_sessions": 15          # Placeholder
        }
        
        return {
            "user_growth_30_days": user_growth,
            "total_assessment_completions": total_completions,
            "system_metrics": system_metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analytics overview: {str(e)}"
        )

@router.get("/content/overview")
async def get_content_overview(current_user: UserModel = Depends(require_admin)):
    """Get content overview for admin dashboard"""
    try:
        db = await get_db()
        
        # Get content statistics
        total_assessments = await db.assessments.count_documents({}) if hasattr(db, 'assessments') else 0
        total_coding_problems = await db.coding_problems.count_documents({}) if hasattr(db, 'coding_problems') else 0
        
        # Get pending content reviews
        pending_reviews = 3  # Placeholder
        
        # Get content quality metrics
        quality_metrics = {
            "avg_rating": 4.2,           # Placeholder
            "completion_rate": 85.5,     # Placeholder
            "user_satisfaction": 4.1     # Placeholder
        }
        
        return {
            "total_assessments": total_assessments,
            "total_coding_problems": total_coding_problems,
            "pending_reviews": pending_reviews,
            "quality_metrics": quality_metrics
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get content overview: {str(e)}"
        )

# User Management Endpoints
@router.get("/users/analytics")
async def get_users_analytics(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    role: Optional[str] = Query(None),
    sort_by: str = Query("activity_score"),
    order: str = Query("desc"),
    current_user: UserModel = Depends(require_admin)
):
    """Get users with analytics data"""
    try:
        db = await get_db()
        
        # Build filter
        filter_dict = {}
        if role:
            filter_dict["role"] = role
        
        # Get users with analytics
        users_cursor = db.users.find(filter_dict, {"password": 0}).skip(offset).limit(limit)
        users = await users_cursor.to_list(length=limit)
        
        # Add analytics data for each user
        user_list = []
        for user in users:
            # Get user's assessment results
            results_cursor = db.results.find({"user_id": user["_id"]}).sort("submitted_at", -1).limit(10)
            results = await results_cursor.to_list(length=10)
            
            # Calculate analytics
            total_logins = 1  # Placeholder
            activity_score = 75.0  # Placeholder
            progress_percentage = 60.0  # Placeholder
            assessments_taken = len(results)
            average_score = sum(r.get("score", 0) for r in results) / len(results) if results else 0
            badges_earned = 2  # Placeholder
            streak_days = 5  # Placeholder
            
            user_list.append({
                "id": str(user["_id"]),
                "name": user.get("name", user.get("username", "Unknown")),
                "email": user.get("email", ""),
                "role": user.get("role", ""),
                "last_login": user.get("last_login", ""),
                "total_logins": total_logins,
                "activity_score": activity_score,
                "progress_percentage": progress_percentage,
                "assessments_taken": assessments_taken,
                "average_score": average_score,
                "badges_earned": badges_earned,
                "streak_days": streak_days
            })
        
        return user_list
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get users analytics: {str(e)}"
        )

@router.get("/users/{user_id}/details")
async def get_user_details(
    user_id: str,
    current_user: UserModel = Depends(require_admin)
):
    """Get detailed user information with analytics"""
    try:
        db = await get_db()
        from bson import ObjectId
        
        # Get user basic info
        user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get user's assessment results
        results_cursor = db.results.find({"user_id": user_id}).sort("submitted_at", -1).limit(20)
        results = await results_cursor.to_list(length=20)
        
        # Calculate analytics
        total_logins = 1  # Placeholder
        activity_score = 75.0  # Placeholder
        progress_percentage = 60.0  # Placeholder
        assessments_taken = len(results)
        average_score = sum(r.get("score", 0) for r in results) / len(results) if results else 0
        badges_earned = 2  # Placeholder
        streak_days = 5  # Placeholder
        
        # Mock recent activity and badges
        recent_activity = [
            {"action": "Completed Assessment", "timestamp": "2024-01-15T10:30:00Z"},
            {"action": "Earned Badge", "timestamp": "2024-01-14T15:20:00Z"},
            {"action": "Logged In", "timestamp": "2024-01-14T09:15:00Z"}
        ]
        
        badges = [
            {"name": "First Assessment", "earned_at": "2024-01-10T14:30:00Z"},
            {"name": "High Scorer", "earned_at": "2024-01-12T16:45:00Z"}
        ]
        
        return {
            "user": {
                "id": str(user_doc["_id"]),
                "name": user_doc.get("name", user_doc.get("username", "Unknown")),
                "email": user_doc.get("email", ""),
                "role": user_doc.get("role", ""),
                "created_at": user_doc.get("created_at", ""),
                "last_login": user_doc.get("last_login", ""),
                "is_active": user_doc.get("is_active", True)
            },
            "analytics": {
                "id": str(user_doc["_id"]),
                "name": user_doc.get("name", user_doc.get("username", "Unknown")),
                "email": user_doc.get("email", ""),
                "role": user_doc.get("role", ""),
                "last_login": user_doc.get("last_login", ""),
                "total_logins": total_logins,
                "activity_score": activity_score,
                "progress_percentage": progress_percentage,
                "assessments_taken": assessments_taken,
                "average_score": average_score,
                "badges_earned": badges_earned,
                "streak_days": streak_days
            },
            "recent_activity": recent_activity,
            "assessment_history": results,
            "badges": badges
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user details: {str(e)}"
        )

@router.post("/users")
async def create_user(
    user_data: dict,
    current_user: UserModel = Depends(require_admin)
):
    """Create a new user"""
    try:
        db = await get_db()
        
        # Check if user already exists
        existing_user = await db.users.find_one({"email": user_data.get("email")})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create user document
        user_doc = {
            "username": user_data.get("username", ""),
            "email": user_data.get("email", ""),
            "name": user_data.get("name", user_data.get("username", "")),
            "role": user_data.get("role", "student"),
            "password": "default_password",  # Should be hashed
            "created_at": datetime.utcnow(),
            "is_active": True
        }
        
        result = await db.users.insert_one(user_doc)
        
        return {
            "success": True,
            "message": "User created successfully",
            "user_id": str(result.inserted_id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )

@router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    user_data: dict,
    current_user: UserModel = Depends(require_admin)
):
    """Update user information"""
    try:
        db = await get_db()
        from bson import ObjectId
        
        # Check if user exists
        user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update user
        update_data = {
            "username": user_data.get("username", user_doc.get("username")),
            "email": user_data.get("email", user_doc.get("email")),
            "name": user_data.get("name", user_doc.get("name")),
            "role": user_data.get("role", user_doc.get("role")),
            "updated_at": datetime.utcnow()
        }
        
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        
        return {
            "success": True,
            "message": "User updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: UserModel = Depends(require_admin)
):
    """Delete a user"""
    try:
        db = await get_db()
        from bson import ObjectId
        
        # Check if user exists
        user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prevent deleting admin users
        if user_doc.get("role") == "admin":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete admin users"
            )
        
        # Delete user
        await db.users.delete_one({"_id": ObjectId(user_id)})
        
        return {
            "success": True,
            "message": "User deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )

# System Analytics Endpoints
@router.get("/analytics/content")
async def get_content_analytics(current_user: UserModel = Depends(require_admin)):
    """Get content analytics for system monitoring"""
    try:
        db = await get_db()
        
        # Get content statistics
        total_assessments = await db.assessments.count_documents({}) if hasattr(db, 'assessments') else 0
        total_coding_problems = await db.coding_problems.count_documents({}) if hasattr(db, 'coding_problems') else 0
        
        # Mock content analytics data
        content_analytics = [
            {
                "content_id": "1",
                "title": "Python Basics Assessment",
                "type": "assessment",
                "creator": "System",
                "views": 150,
                "completions": 120,
                "average_score": 78.5,
                "popularity_score": 85.2,
                "difficulty_rating": 3.2,
                "last_updated": "2024-01-15T10:30:00Z"
            },
            {
                "content_id": "2", 
                "title": "JavaScript Fundamentals",
                "type": "assessment",
                "creator": "System",
                "views": 200,
                "completions": 180,
                "average_score": 82.1,
                "popularity_score": 92.3,
                "difficulty_rating": 2.8,
                "last_updated": "2024-01-14T15:20:00Z"
            },
            {
                "content_id": "3",
                "title": "Data Structures Challenge",
                "type": "coding_problem",
                "creator": "System", 
                "views": 95,
                "completions": 60,
                "average_score": 65.4,
                "popularity_score": 72.1,
                "difficulty_rating": 4.1,
                "last_updated": "2024-01-13T09:15:00Z"
            }
        ]
        
        return {
            "total_content": total_assessments + total_coding_problems,
            "content_analytics": content_analytics,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get content analytics: {str(e)}"
        )

@router.get("/analytics/teachers")
async def get_teacher_performance(current_user: UserModel = Depends(require_admin)):
    """Get teacher performance analytics"""
    try:
        db = await get_db()
        
        # Get teachers
        teachers_cursor = db.users.find({"role": "teacher"})
        teachers = await teachers_cursor.to_list(length=100)
        
        # Calculate teacher performance metrics
        teacher_performance = []
        for teacher in teachers:
            # Get teacher's batches
            batches_cursor = db.batches.find({"teacher_id": teacher["_id"]})
            batches = await batches_cursor.to_list(length=100)
            
            # Get students in teacher's batches
            total_students = 0
            for batch in batches:
                student_count = await db.users.count_documents({"batch_id": batch["_id"]})
                total_students += student_count
            
            # Get assessment completions for teacher's students
            total_completions = 0
            for batch in batches:
                completions = await db.results.count_documents({"batch_id": batch["_id"]})
                total_completions += completions
            
            # Calculate performance metrics
            performance_score = min(100, (total_students * 10) + (total_completions * 5))
            engagement_rate = (total_completions / max(total_students, 1)) * 100
            
            teacher_performance.append({
                "teacher_id": str(teacher["_id"]),
                "name": teacher.get("name", teacher.get("username", "Unknown")),
                "email": teacher.get("email", ""),
                "total_batches": len(batches),
                "total_students": total_students,
                "total_completions": total_completions,
                "performance_score": performance_score,
                "engagement_rate": engagement_rate,
                "last_active": teacher.get("last_login", ""),
                "created_at": teacher.get("created_at", "")
            })
        
        return {
            "total_teachers": len(teachers),
            "teacher_performance": teacher_performance,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get teacher performance: {str(e)}"
        )

@router.get("/analytics/performance")
async def get_system_performance(current_user: UserModel = Depends(require_admin)):
    """Get system performance metrics"""
    try:
        db = await get_db()
        
        # Test database performance
        start_time = datetime.utcnow()
        await db.command("ping")
        db_response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Get system metrics
        system_metrics = {
            "database_response_time": f"{db_response_time:.2f}ms",
            "api_response_time": "45ms",  # Placeholder
            "memory_usage": "65%",        # Placeholder
            "cpu_usage": "23%",           # Placeholder
            "disk_usage": "42%",          # Placeholder
            "uptime": "99.9%",           # Placeholder
            "error_rate": "0.1%",        # Placeholder
            "active_connections": 15      # Placeholder
        }
        
        # Get user activity metrics
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = today - timedelta(days=7)
        
        active_today = await db.users.count_documents({
            "last_login": {"$gte": today}
        })
        active_week = await db.users.count_documents({
            "last_login": {"$gte": week_ago}
        })
        
        # Get content metrics
        total_assessments = await db.assessments.count_documents({}) if hasattr(db, 'assessments') else 0
        total_results = await db.results.count_documents({}) if hasattr(db, 'results') else 0
        
        return {
            "system_metrics": system_metrics,
            "user_activity": {
                "active_today": active_today,
                "active_week": active_week,
                "total_assessments": total_assessments,
                "total_completions": total_results
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system performance: {str(e)}"
        )

# Content Oversight Endpoints
@router.get("/content/library")
async def get_content_library(
    content_type: Optional[str] = Query(None),
    subject: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    current_user: UserModel = Depends(require_admin)
):
    """Get content library for oversight"""
    try:
        db = await get_db()
        
        # Build filter
        filter_dict = {}
        if content_type:
            filter_dict["type"] = content_type
        if subject:
            filter_dict["subject"] = subject
        if difficulty:
            filter_dict["difficulty"] = difficulty
        
        # Get assessments
        assessments_cursor = db.assessments.find(filter_dict)
        assessments = await assessments_cursor.to_list(length=100)
        
        # Get coding problems
        coding_cursor = db.coding_problems.find(filter_dict)
        coding_problems = await coding_cursor.to_list(length=100)
        
        # Format content items
        content_items = []
        
        for assessment in assessments:
            content_items.append({
                "id": str(assessment["_id"]),
                "title": assessment.get("title", "Untitled Assessment"),
                "type": "assessment",
                "subject": assessment.get("subject", "General"),
                "difficulty": assessment.get("difficulty", "medium"),
                "creator": assessment.get("creator", "System"),
                "status": assessment.get("status", "active"),
                "created_at": assessment.get("created_at", ""),
                "views": assessment.get("views", 0),
                "downloads": assessment.get("downloads", 0)
            })
        
        for problem in coding_problems:
            content_items.append({
                "id": str(problem["_id"]),
                "title": problem.get("title", "Untitled Problem"),
                "type": "coding_problem",
                "subject": problem.get("subject", "Programming"),
                "difficulty": problem.get("difficulty", "medium"),
                "creator": problem.get("creator", "System"),
                "status": problem.get("status", "active"),
                "created_at": problem.get("created_at", ""),
                "views": problem.get("views", 0),
                "downloads": problem.get("downloads", 0)
            })
        
        return {
            "content_items": content_items,
            "total_items": len(content_items),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get content library: {str(e)}"
        )

@router.get("/content/curation")
async def get_content_curation(
    status: Optional[str] = Query(None),
    current_user: UserModel = Depends(require_admin)
):
    """Get content curation data"""
    try:
        db = await get_db()
        
        # Mock content curation data
        curation_items = [
            {
                "content_id": "1",
                "title": "Python Basics Assessment",
                "type": "assessment",
                "creator": "System",
                "status": "pending_review",
                "review_notes": "Needs difficulty adjustment",
                "quality_score": 7.5,
                "difficulty_level": "beginner",
                "subject": "Python Programming",
                "created_at": "2024-01-15T10:30:00Z",
                "reviewed_at": None
            },
            {
                "content_id": "2",
                "title": "JavaScript Fundamentals",
                "type": "assessment", 
                "creator": "System",
                "status": "approved",
                "review_notes": "High quality content",
                "quality_score": 9.2,
                "difficulty_level": "intermediate",
                "subject": "JavaScript",
                "created_at": "2024-01-14T15:20:00Z",
                "reviewed_at": "2024-01-14T16:30:00Z"
            },
            {
                "content_id": "3",
                "title": "Data Structures Challenge",
                "type": "coding_problem",
                "creator": "System",
                "status": "rejected",
                "review_notes": "Too complex for target audience",
                "quality_score": 6.8,
                "difficulty_level": "advanced",
                "subject": "Data Structures",
                "created_at": "2024-01-13T09:15:00Z",
                "reviewed_at": "2024-01-13T11:45:00Z"
            }
        ]
        
        # Filter by status if provided
        if status:
            curation_items = [item for item in curation_items if item["status"] == status]
        
        return {
            "curation_items": curation_items,
            "total_items": len(curation_items),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get content curation: {str(e)}"
        )

@router.post("/content/{content_id}/approve")
async def approve_content(
    content_id: str,
    review_data: dict,
    current_user: UserModel = Depends(require_admin)
):
    """Approve content for publication"""
    try:
        db = await get_db()
        from bson import ObjectId
        
        # Update content status
        update_data = {
            "status": "approved",
            "reviewed_by": current_user.id,
            "reviewed_at": datetime.utcnow(),
            "review_notes": review_data.get("review_notes", "")
        }
        
        # Try to update in assessments collection
        result = await db.assessments.update_one(
            {"_id": ObjectId(content_id)},
            {"$set": update_data}
        )
        
        # If not found in assessments, try coding_problems
        if result.matched_count == 0:
            result = await db.coding_problems.update_one(
                {"_id": ObjectId(content_id)},
                {"$set": update_data}
            )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )
        
        return {
            "success": True,
            "message": "Content approved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve content: {str(e)}"
        )

@router.post("/content/{content_id}/reject")
async def reject_content(
    content_id: str,
    review_data: dict,
    current_user: UserModel = Depends(require_admin)
):
    """Reject content"""
    try:
        db = await get_db()
        from bson import ObjectId
        
        # Update content status
        update_data = {
            "status": "rejected",
            "reviewed_by": current_user.id,
            "reviewed_at": datetime.utcnow(),
            "review_notes": review_data.get("review_notes", "")
        }
        
        # Try to update in assessments collection
        result = await db.assessments.update_one(
            {"_id": ObjectId(content_id)},
            {"$set": update_data}
        )
        
        # If not found in assessments, try coding_problems
        if result.matched_count == 0:
            result = await db.coding_problems.update_one(
                {"_id": ObjectId(content_id)},
                {"$set": update_data}
            )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )
        
        return {
            "success": True,
            "message": "Content rejected successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reject content: {str(e)}"
        )
