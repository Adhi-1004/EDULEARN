"""
User management endpoints
Handles user CRUD operations, profile management, and user-specific features
"""
from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr

from ..core.security import security_manager
from ..db import get_db
from ..schemas.schemas import UserCreate, UserResponse, UserUpdate
from ..models.models import UserModel
from ..dependencies import get_current_user, require_admin, require_teacher_or_admin

router = APIRouter()

# Response Models
class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
    page: int
    size: int

class UserStatsResponse(BaseModel):
    total_users: int
    active_users: int
    new_users_today: int
    users_by_role: Dict[str, int]

class UserProfileResponse(BaseModel):
    user: UserResponse
    stats: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None

class GamificationResponse(BaseModel):
    xp: int
    level: int
    streak: int
    badges: List[str]
    achievements: List[str]

class BadgeResponse(BaseModel):
    id: str
    name: str
    description: str
    icon: str
    earned: bool
    earned_at: Optional[datetime] = None

@router.get("/", response_model=UserListResponse)
async def get_users(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    role: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: UserModel = Depends(require_admin)
):
    """Get paginated list of users (Admin only)"""
    try:
        db = await get_db()
        
        # Build filter
        filter_dict = {}
        if role:
            filter_dict["role"] = role
        if search:
            filter_dict["$or"] = [
                {"username": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}}
            ]
        
        # Get total count
        total = await db.users.count_documents(filter_dict)
        
        # Get users with pagination
        skip = (page - 1) * size
        users_cursor = db.users.find(filter_dict).skip(skip).limit(size)
        users = []
        
        async for user_doc in users_cursor:
            users.append(UserResponse(**{k: v for k, v in user_doc.items() if k != "password"}))
        
        return UserListResponse(
            users=users,
            total=total,
            page=page,
            size=size
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get users: {str(e)}"
        )

@router.get("/me", response_model=UserProfileResponse)
async def get_my_profile(current_user: UserModel = Depends(get_current_user)):
    """Get current user's profile"""
    try:
        db = await get_db()
        
        # Get user stats if available
        stats = None
        if current_user.role in ["student", "teacher"]:
            # Get user-specific stats
            stats = {
                "total_assignments": 0,  # Placeholder
                "completed_assignments": 0,  # Placeholder
                "average_score": 0.0  # Placeholder
            }
        
        return UserProfileResponse(
            user=UserResponse(**current_user.dict()),
            stats=stats
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get profile: {str(e)}"
        )

@router.put("/me", response_model=UserResponse)
async def update_my_profile(
    user_update: UserUpdate,
    current_user: UserModel = Depends(get_current_user)
):
    """Update current user's profile"""
    try:
        db = await get_db()
        
        # Prepare update data
        update_data = user_update.dict(exclude_unset=True)
        if not update_data:
            return UserResponse(**current_user.dict())
        
        # Update user
        await db.users.update_one(
            {"_id": current_user.id},
            {"$set": {**update_data, "updated_at": datetime.utcnow()}}
        )
        
        # Get updated user
        updated_user = await db.users.find_one({"_id": current_user.id})
        return UserResponse(**{k: v for k, v in updated_user.items() if k != "password"})
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: UserModel = Depends(require_teacher_or_admin)
):
    """Get specific user by ID (Teacher/Admin only)"""
    try:
        db = await get_db()
        
        user_doc = await db.users.find_one({"_id": user_id})
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(**{k: v for k, v in user_doc.items() if k != "password"})
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user: {str(e)}"
        )

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: UserModel = Depends(require_admin)
):
    """Update user by ID (Admin only)"""
    try:
        db = await get_db()
        
        # Check if user exists
        existing_user = await db.users.find_one({"_id": user_id})
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prepare update data
        update_data = user_update.dict(exclude_unset=True)
        if not update_data:
            return UserResponse(**{k: v for k, v in existing_user.items() if k != "password"})
        
        # Update user
        await db.users.update_one(
            {"_id": user_id},
            {"$set": {**update_data, "updated_at": datetime.utcnow()}}
        )
        
        # Get updated user
        updated_user = await db.users.find_one({"_id": user_id})
        return UserResponse(**{k: v for k, v in updated_user.items() if k != "password"})
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current_user: UserModel = Depends(require_admin)
):
    """Delete user by ID (Admin only)"""
    try:
        db = await get_db()
        
        # Check if user exists
        existing_user = await db.users.find_one({"_id": user_id})
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Soft delete (set is_active to False)
        await db.users.update_one(
            {"_id": user_id},
            {"$set": {"is_active": False, "deleted_at": datetime.utcnow()}}
        )
        
        return {"message": "User deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )

@router.get("/stats/overview", response_model=UserStatsResponse)
async def get_user_stats(current_user: UserModel = Depends(require_admin)):
    """Get user statistics overview (Admin only)"""
    try:
        db = await get_db()
        
        # Get total users
        total_users = await db.users.count_documents({})
        
        # Get active users (logged in within last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        active_users = await db.users.count_documents({
            "last_login": {"$gte": thirty_days_ago}
        })
        
        # Get new users today
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        new_users_today = await db.users.count_documents({
            "created_at": {"$gte": today}
        })
        
        # Get users by role
        pipeline = [
            {"$group": {"_id": "$role", "count": {"$sum": 1}}}
        ]
        users_by_role = {}
        async for doc in db.users.aggregate(pipeline):
            users_by_role[doc["_id"]] = doc["count"]
        
        return UserStatsResponse(
            total_users=total_users,
            active_users=active_users,
            new_users_today=new_users_today,
            users_by_role=users_by_role
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user stats: {str(e)}"
        )

# Gamification endpoints
@router.get("/{user_id}/gamification", response_model=GamificationResponse)
async def get_user_gamification(
    user_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """Get user gamification data (XP, level, streak, badges)"""
    try:
        # Verify user can access this data
        if current_user.id != user_id and current_user.role not in ["admin", "teacher"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this user's gamification data"
            )
        
        db = await get_db()
        user_doc = await db.users.find_one({"_id": user_id})
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Return gamification data (with defaults if not set)
        return GamificationResponse(
            xp=user_doc.get("xp", 0),
            level=user_doc.get("level", 1),
            streak=user_doc.get("streak", 0),
            badges=user_doc.get("badges", []),
            achievements=user_doc.get("achievements", [])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get gamification data: {str(e)}"
        )

@router.get("/{user_id}/badges", response_model=List[BadgeResponse])
async def get_user_badges(
    user_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """Get user badges"""
    try:
        # Verify user can access this data
        if current_user.id != user_id and current_user.role not in ["admin", "teacher"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this user's badges"
            )
        
        db = await get_db()
        user_doc = await db.users.find_one({"_id": user_id})
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get user's earned badges
        earned_badges = user_doc.get("badges", [])
        
        # Define available badges
        available_badges = [
            {"id": "first_login", "name": "Welcome", "description": "First login", "icon": "🎉"},
            {"id": "first_test", "name": "Test Taker", "description": "Completed first test", "icon": "📝"},
            {"id": "perfect_score", "name": "Perfectionist", "description": "Got 100% on a test", "icon": "💯"},
            {"id": "streak_7", "name": "Week Warrior", "description": "7-day streak", "icon": "🔥"},
            {"id": "streak_30", "name": "Month Master", "description": "30-day streak", "icon": "👑"},
            {"id": "coding_expert", "name": "Code Master", "description": "Solved 10 coding problems", "icon": "💻"},
        ]
        
        badges = []
        for badge in available_badges:
            badges.append(BadgeResponse(
                id=badge["id"],
                name=badge["name"],
                description=badge["description"],
                icon=badge["icon"],
                earned=badge["id"] in earned_badges,
                earned_at=user_doc.get("badge_earned_at", {}).get(badge["id"])
            ))
        
        return badges
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user badges: {str(e)}"
        )

@router.post("/{user_id}/update-activity")
async def update_user_activity(
    user_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """Update user activity (for streak tracking)"""
    try:
        # Verify user can update this data
        if current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this user's activity"
            )
        
        db = await get_db()
        
        # Update last activity and increment streak if it's a new day
        now = datetime.utcnow()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        user_doc = await db.users.find_one({"_id": user_id})
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        last_activity = user_doc.get("last_activity")
        if last_activity:
            last_activity_date = last_activity.replace(hour=0, minute=0, second=0, microsecond=0)
            if last_activity_date < today:
                # New day - increment streak
                await db.users.update_one(
                    {"_id": user_id},
                    {
                        "$set": {"last_activity": now},
                        "$inc": {"streak": 1}
                    }
                )
            else:
                # Same day - just update activity time
                await db.users.update_one(
                    {"_id": user_id},
                    {"$set": {"last_activity": now}}
                )
        else:
            # First activity
            await db.users.update_one(
                {"_id": user_id},
                {
                    "$set": {"last_activity": now},
                    "$inc": {"streak": 1}
                }
            )
        
        return {"success": True, "message": "Activity updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user activity: {str(e)}"
        )
