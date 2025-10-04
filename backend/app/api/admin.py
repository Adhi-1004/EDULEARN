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
    active_users: int
    total_teachers: int
    total_students: int
    total_assessments: int
    total_coding_problems: int
    platform_health: str

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

@router.get("/stats/platform", response_model=PlatformStatsResponse)
async def get_platform_stats(current_user: UserModel = Depends(require_admin)):
    """Get comprehensive platform statistics"""
    try:
        db = await get_db()
        
        # Get user counts by role
        total_users = await db.users.count_documents({})
        active_users = await db.users.count_documents({
            "last_login": {"$gte": datetime.utcnow() - timedelta(days=30)}
        })
        total_teachers = await db.users.count_documents({"role": "teacher"})
        total_students = await db.users.count_documents({"role": "student"})
        
        # Get content counts (placeholders for now)
        total_assessments = await db.assessments.count_documents({}) if hasattr(db, 'assessments') else 0
        total_coding_problems = await db.coding_problems.count_documents({}) if hasattr(db, 'coding_problems') else 0
        
        # Calculate platform health
        health_score = 0
        if total_users > 0:
            health_score += 20
        if active_users > 0:
            health_score += 30
        if total_teachers > 0:
            health_score += 25
        if total_students > 0:
            health_score += 25
        
        platform_health = "excellent" if health_score >= 80 else "good" if health_score >= 60 else "needs_attention"
        
        return PlatformStatsResponse(
            total_users=total_users,
            active_users=active_users,
            total_teachers=total_teachers,
            total_students=total_students,
            total_assessments=total_assessments,
            total_coding_problems=total_coding_problems,
            platform_health=platform_health
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
