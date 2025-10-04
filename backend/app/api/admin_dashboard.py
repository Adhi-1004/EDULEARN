from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
from pydantic import BaseModel
from ..db import get_db
from ..schemas import UserCreate, UserResponse
from ..models import UserModel
from ..dependencies import require_admin_only, require_user_management, require_platform_management, require_analytics_access
import os

router = APIRouter(prefix="/admin", tags=["admin_dashboard"])
security = HTTPBearer()

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"

async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token - admin role required"""
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
        
        # Check if user is an admin
        user_role = user.get("role", "student")
        if user_role != "admin":
            raise HTTPException(status_code=403, detail="Access denied. Admin role required.")
        
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

# User Management Models
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    is_admin: Optional[bool] = None

class UserCreateResponse(BaseModel):
    id: str
    email: str
    username: Optional[str] = None
    name: Optional[str] = None
    profile_picture: Optional[str] = None
    is_admin: bool = False
    role: str = "student"
    password: Optional[str] = None

class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
    page: int
    per_page: int

# Analytics Models
class PlatformStats(BaseModel):
    total_users: int
    total_students: int
    total_teachers: int
    total_admins: int
    active_users_today: int
    assessments_taken_today: int
    total_assessments: int

class UserActivity(BaseModel):
    user_id: str
    user_name: str
    email: str
    role: str
    last_active: str
    assessments_taken: int

class ContentStats(BaseModel):
    total_questions: int
    total_coding_problems: int
    popular_topics: List[Dict[str, Any]]
    least_popular_topics: List[Dict[str, Any]]

# Admin Dashboard Endpoints

@router.get("/users", response_model=UserListResponse)
async def get_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, le=100),
    role: Optional[str] = None,
    search: Optional[str] = None,
    admin: dict = Depends(require_user_management)
):
    """Get list of all users with pagination and filtering"""
    try:
        db = await get_db()
        
        # Build query
        query = {}
        if role:
            query["role"] = role
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}}
            ]
        
        # Calculate pagination
        skip = (page - 1) * per_page
        
        # Get users with pagination
        users_cursor = await db.users.find(query).skip(skip).limit(per_page).to_list(None)
        total_users = await db.users.count_documents(query)
        
        # Convert to response format
        users_response = []
        for user in users_cursor:
            user_response = UserResponse(
                id=str(user["_id"]),
                email=user["email"],
                username=user.get("username"),
                name=user.get("name"),
                profile_picture=user.get("profile_picture"),
                is_admin=user.get("is_admin", False),
                role=user.get("role", "student")
            )
            users_response.append(user_response)
        
        return UserListResponse(
            users=users_response,
            total=total_users,
            page=page,
            per_page=per_page
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/users", response_model=UserCreateResponse)
async def create_user(user_data: UserCreate, admin: dict = Depends(require_user_management)):
    """Create a new user"""
    try:
        db = await get_db()
        
        # Check if user already exists
        existing_user = await db.users.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists")
        
        # Hash password if provided
        hashed_password = None
        if user_data.password:
            hashed_password = UserModel.hash_password(user_data.password)
        
        # Create user document
        user_doc = {
            "username": user_data.username,
            "email": user_data.email,
            "password": hashed_password,
            "is_admin": user_data.role == "admin",
            "role": user_data.role or "student",
            "google_id": user_data.google_id,
            "name": user_data.name,
            "profile_picture": user_data.profile_picture,
            "face_descriptor": None
        }
        
        # Insert user
        result = await db.users.insert_one(user_doc)
        user_doc["_id"] = result.inserted_id
        
        return UserCreateResponse(
            id=str(user_doc["_id"]),
            email=user_doc["email"],
            username=user_doc.get("username"),
            name=user_doc.get("name"),
            profile_picture=user_doc.get("profile_picture"),
            is_admin=user_doc.get("is_admin", False),
            role=user_doc.get("role", "student")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, admin: dict = Depends(require_user_management)):
    """Get details of a specific user"""
    try:
        db = await get_db()
        
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID")
        
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse(
            id=str(user["_id"]),
            email=user["email"],
            username=user.get("username"),
            name=user.get("name"),
            profile_picture=user.get("profile_picture"),
            is_admin=user.get("is_admin", False),
            role=user.get("role", "student")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user_data: UserUpdate, admin: dict = Depends(require_user_management)):
    """Update a user's information"""
    try:
        db = await get_db()
        
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID")
        
        # Check if user exists
        existing_user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Build update document
        update_doc = {}
        if user_data.name is not None:
            update_doc["name"] = user_data.name
        if user_data.email is not None:
            # Check if email is already taken by another user
            if user_data.email != existing_user["email"]:
                email_check = await db.users.find_one({"email": user_data.email, "_id": {"$ne": ObjectId(user_id)}})
                if email_check:
                    raise HTTPException(status_code=400, detail="Email already in use")
            update_doc["email"] = user_data.email
        if user_data.role is not None:
            update_doc["role"] = user_data.role
            update_doc["is_admin"] = user_data.role == "admin"
        
        # Update user
        await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": update_doc})
        
        # Get updated user
        updated_user = await db.users.find_one({"_id": ObjectId(user_id)})
        
        return UserResponse(
            id=str(updated_user["_id"]),
            email=updated_user["email"],
            username=updated_user.get("username"),
            name=updated_user.get("name"),
            profile_picture=updated_user.get("profile_picture"),
            is_admin=updated_user.get("is_admin", False),
            role=updated_user.get("role", "student")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/users/{user_id}")
async def delete_user(user_id: str, admin: dict = Depends(require_user_management)):
    """Delete a user"""
    try:
        db = await get_db()
        
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID")
        
        # Check if user exists
        existing_user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Delete user
        await db.users.delete_one({"_id": ObjectId(user_id)})
        
        return {"success": True, "message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Analytics Endpoints

@router.get("/analytics/platform", response_model=PlatformStats)
async def get_platform_stats(admin: dict = Depends(require_analytics_access)):
    """Get platform-wide statistics"""
    try:
        db = await get_db()
        
        # Get user counts by role
        total_users = await db.users.count_documents({})
        total_students = await db.users.count_documents({"role": "student"})
        total_teachers = await db.users.count_documents({"role": "teacher"})
        total_admins = await db.users.count_documents({"role": "admin"})
        
        # Get active users (users who took assessments today)
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        active_users_today = await db.results.count_documents({"date": {"$gte": today}})
        
        # Get assessment counts
        total_assessments = await db.results.count_documents({})
        assessments_taken_today = await db.results.count_documents({"date": {"$gte": today}})
        
        return PlatformStats(
            total_users=total_users,
            total_students=total_students,
            total_teachers=total_teachers,
            total_admins=total_admins,
            active_users_today=active_users_today,
            assessments_taken_today=assessments_taken_today,
            total_assessments=total_assessments
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/users", response_model=List[UserActivity])
async def get_user_activity(admin: dict = Depends(require_analytics_access)):
    """Get user activity data"""
    try:
        db = await get_db()
        
        # Get all users
        users_cursor = await db.users.find({}).to_list(None)
        user_activities = []
        
        for user in users_cursor:
            # Get assessment count for user
            assessment_count = await db.results.count_documents({"user_id": str(user["_id"])})
            
            # Get last assessment date
            last_assessment = await db.results.find_one(
                {"user_id": str(user["_id"])}, 
                sort=[("date", -1)]
            )
            
            last_active = ""
            if last_assessment:
                last_active = last_assessment["date"].isoformat() if isinstance(last_assessment["date"], datetime) else str(last_assessment["date"])
            
            user_activity = UserActivity(
                user_id=str(user["_id"]),
                user_name=user.get("name", "Unknown"),
                email=user["email"],
                role=user.get("role", "student"),
                last_active=last_active,
                assessments_taken=assessment_count
            )
            user_activities.append(user_activity)
        
        # Sort by last active (descending)
        user_activities.sort(key=lambda x: x.last_active, reverse=True)
        
        return user_activities[:50]  # Return top 50 most active users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/content", response_model=ContentStats)
async def get_content_stats(admin: dict = Depends(require_analytics_access)):
    """Get content-related statistics"""
    try:
        db = await get_db()
        
        # Get question counts
        total_questions = await db.questions.count_documents({})
        total_coding_problems = await db.coding_problems.count_documents({})
        
        # Get popular topics (based on assessment results)
        pipeline = [
            {"$group": {"_id": "$topic", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        popular_topics_cursor = await db.results.aggregate(pipeline).to_list(None)
        popular_topics = [{"topic": item["_id"], "count": item["count"]} for item in popular_topics_cursor]
        
        # Get least popular topics
        least_popular_topics_cursor = await db.results.aggregate([
            {"$group": {"_id": "$topic", "count": {"$sum": 1}}},
            {"$sort": {"count": 1}},
            {"$limit": 10}
        ]).to_list(None)
        least_popular_topics = [{"topic": item["_id"], "count": item["count"]} for item in least_popular_topics_cursor]
        
        return ContentStats(
            total_questions=total_questions,
            total_coding_problems=total_coding_problems,
            popular_topics=popular_topics,
            least_popular_topics=least_popular_topics
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# System Management Endpoints

@router.get("/system/health")
async def system_health_check(admin: dict = Depends(require_platform_management)):
    """Check system health"""
    try:
        db = await get_db()
        
        # Check database connection
        db_status = "healthy"
        try:
            await db.command("ping")
        except Exception:
            db_status = "unhealthy"
        
        return {
            "status": "healthy" if db_status == "healthy" else "degraded",
            "database": db_status,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))