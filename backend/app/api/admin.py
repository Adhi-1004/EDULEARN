"""
Admin Dashboard Router
Handles all admin-specific endpoints for platform management
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
import asyncio

from ..db import get_db
from .endpoints.auth import get_current_user
from ..dependencies import require_admin
from ..schemas import UserCreate, UserResponse

router = APIRouter()

# Admin Dashboard Metrics Endpoints

@router.get("/metrics/overview")
async def get_admin_metrics(user: dict = Depends(require_admin)):
    """Get high-level platform metrics for admin dashboard"""
    try:
        db = await get_db()
        
        # Calculate date ranges
        now = datetime.utcnow()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        last_30d = now - timedelta(days=30)
        
        # Total users by role
        total_users = await db.users.count_documents({})
        total_students = await db.users.count_documents({"role": "student"})
        total_teachers = await db.users.count_documents({"role": "teacher"})
        total_admins = await db.users.count_documents({"role": "admin"})
        
        # Active users in last 24h (users who have results or coding solutions)
        active_users_24h = set()
        
        # Get users from recent results
        recent_results = await db.results.find({
            "date": {"$gte": last_24h}
        }).to_list(None)
        for result in recent_results:
            active_users_24h.add(str(result["user_id"]))
        
        # Get users from recent coding solutions
        recent_coding_solutions = await db.coding_solutions.find({
            "submitted_at": {"$gte": last_24h}
        }).to_list(None)
        for solution in recent_coding_solutions:
            active_users_24h.add(str(solution["user_id"]))
        
        active_users_count = len(active_users_24h)
        
        # Assessments completed
        assessments_completed = await db.results.count_documents({})
        
        # Coding submissions
        coding_submissions = await db.coding_solutions.count_documents({})
        
        # Recent activity (last 10 activities)
        recent_activities = []
        
        # Get recent user registrations
        recent_users = await db.users.find({
            "created_at": {"$gte": last_7d}
        }).sort("created_at", -1).limit(5).to_list(None)
        
        for user_doc in recent_users:
            recent_activities.append({
                "type": "user_registration",
                "message": f"New {user_doc.get('role', 'student')} registered: {user_doc.get('username', user_doc.get('email', 'Unknown'))}",
                "timestamp": user_doc.get('created_at', datetime.utcnow()),
                "user_id": str(user_doc["_id"]),
                "role": user_doc.get('role', 'student')
            })
        
        # Get recent assessment completions
        recent_assessments = await db.results.find({
            "date": {"$gte": last_24h}
        }).sort("date", -1).limit(5).to_list(None)
        
        for result in recent_assessments:
            user_doc = await db.users.find_one({"_id": result["user_id"]})
            if user_doc:
                recent_activities.append({
                    "type": "assessment_completed",
                    "message": f"{user_doc.get('username', user_doc.get('email', 'Student'))} completed {result.get('topic', 'Assessment')}",
                    "timestamp": result["date"],
                    "user_id": str(result["user_id"]),
                    "score": result.get("score", 0),
                    "total": result.get("total_questions", 0)
                })
        
        # Get recent coding submissions
        recent_coding = await db.coding_solutions.find({
            "submitted_at": {"$gte": last_24h}
        }).sort("submitted_at", -1).limit(5).to_list(None)
        
        for solution in recent_coding:
            user_doc = await db.users.find_one({"_id": solution["user_id"]})
            if user_doc:
                recent_activities.append({
                    "type": "coding_submission",
                    "message": f"{user_doc.get('username', user_doc.get('email', 'Student'))} submitted coding solution",
                    "timestamp": solution["submitted_at"],
                    "user_id": str(solution["user_id"]),
                    "status": solution.get("status", "unknown")
                })
        
        # Sort activities by timestamp
        recent_activities.sort(key=lambda x: x["timestamp"], reverse=True)
        recent_activities = recent_activities[:10]
        
        # User registration chart data (last 30 days)
        registration_data = []
        for i in range(30):
            date = now - timedelta(days=i)
            start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)
            
            students_count = await db.users.count_documents({
                "role": "student",
                "created_at": {"$gte": start_of_day, "$lt": end_of_day}
            })
            
            teachers_count = await db.users.count_documents({
                "role": "teacher", 
                "created_at": {"$gte": start_of_day, "$lt": end_of_day}
            })
            
            registration_data.append({
                "date": start_of_day.strftime("%Y-%m-%d"),
                "students": students_count,
                "teachers": teachers_count,
                "total": students_count + teachers_count
            })
        
        registration_data.reverse()  # Show oldest to newest
        
        return {
            "success": True,
            "metrics": {
                "total_users": total_users,
                "total_students": total_students,
                "total_teachers": total_teachers,
                "total_admins": total_admins,
                "active_users_24h": active_users_count,
                "assessments_completed": assessments_completed,
                "coding_submissions": coding_submissions
            },
            "recent_activities": recent_activities,
            "registration_chart": registration_data
        }
        
    except Exception as e:
        print(f"[ERROR] [ADMIN] Error fetching metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch admin metrics: {str(e)}")

@router.get("/users")
async def get_all_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    user: dict = Depends(require_admin)
):
    """Get all users with pagination, search, and filtering"""
    try:
        db = await get_db()
        
        # Build query
        query = {}
        if search:
            query["$or"] = [
                {"username": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}},
                {"name": {"$regex": search, "$options": "i"}}
            ]
        
        if role:
            query["role"] = role
        
        # Build sort
        sort_direction = -1 if sort_order == "desc" else 1
        sort_criteria = [(sort_by, sort_direction)]
        
        # Get total count
        total_users = await db.users.count_documents(query)
        
        # Get users with pagination
        skip = (page - 1) * limit
        users = await db.users.find(query).sort(sort_criteria).skip(skip).limit(limit).to_list(None)
        
        # Format users
        formatted_users = []
        for user_doc in users:
            # Get last login from recent activity
            last_login = None
            recent_result = await db.results.find_one(
                {"user_id": user_doc["_id"]},
                sort=[("date", -1)]
            )
            if recent_result:
                last_login = recent_result["date"]
            
            formatted_users.append({
                "id": str(user_doc["_id"]),
                "username": user_doc.get("username"),
                "email": user_doc.get("email"),
                "name": user_doc.get("name"),
                "role": user_doc.get("role", "student"),
                "is_admin": user_doc.get("is_admin", False),
                "created_at": user_doc.get("created_at", datetime.utcnow()),
                "last_login": last_login,
                "profile_picture": user_doc.get("profile_picture")
            })
        
        return {
            "success": True,
            "users": formatted_users,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_users,
                "pages": (total_users + limit - 1) // limit
            }
        }
        
    except Exception as e:
        print(f"[ERROR] [ADMIN] Error fetching users: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch users: {str(e)}")

@router.get("/users/{user_id}")
async def get_user_details(user_id: str, user: dict = Depends(require_admin)):
    """Get detailed user information"""
    try:
        db = await get_db()
        
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID")
        
        user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user_doc:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user statistics
        total_assessments = await db.results.count_documents({"user_id": ObjectId(user_id)})
        total_coding_submissions = await db.coding_solutions.count_documents({"user_id": ObjectId(user_id)})
        
        # Get recent activity
        recent_results = await db.results.find(
            {"user_id": ObjectId(user_id)}
        ).sort("date", -1).limit(10).to_list(None)
        
        recent_coding = await db.coding_solutions.find(
            {"user_id": ObjectId(user_id)}
        ).sort("submitted_at", -1).limit(10).to_list(None)
        
        return {
            "success": True,
            "user": {
                "id": str(user_doc["_id"]),
                "username": user_doc.get("username"),
                "email": user_doc.get("email"),
                "name": user_doc.get("name"),
                "role": user_doc.get("role", "student"),
                "is_admin": user_doc.get("is_admin", False),
                "created_at": user_doc.get("created_at"),
                "profile_picture": user_doc.get("profile_picture"),
                "statistics": {
                    "total_assessments": total_assessments,
                    "total_coding_submissions": total_coding_submissions
                },
                "recent_activity": {
                    "assessments": recent_results,
                    "coding_submissions": recent_coding
                }
            }
        }
        
    except Exception as e:
        print(f"[ERROR] [ADMIN] Error fetching user details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch user details: {str(e)}")

@router.put("/users/{user_id}")
async def update_user(
    user_id: str, 
    update_data: Dict[str, Any], 
    user: dict = Depends(require_admin)
):
    """Update user information"""
    try:
        db = await get_db()
        
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID")
        
        # Check if user exists
        existing_user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Prepare update data
        update_fields = {}
        allowed_fields = ["username", "email", "name", "role", "is_admin"]
        
        for field in allowed_fields:
            if field in update_data:
                update_fields[field] = update_data[field]
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No valid fields to update")
        
        # Update user
        result = await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_fields}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="No changes made")
        
        return {
            "success": True,
            "message": "User updated successfully"
        }
        
    except Exception as e:
        print(f"[ERROR] [ADMIN] Error updating user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")

@router.delete("/users/{user_id}")
async def delete_user(user_id: str, user: dict = Depends(require_admin)):
    """Delete a user"""
    try:
        db = await get_db()
        
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID")
        
        # Check if user exists
        existing_user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Prevent deleting the last admin
        if existing_user.get("role") == "admin":
            admin_count = await db.users.count_documents({"role": "admin"})
            if admin_count <= 1:
                raise HTTPException(status_code=400, detail="Cannot delete the last admin user")
        
        # Delete user and related data
        await db.users.delete_one({"_id": ObjectId(user_id)})
        await db.results.delete_many({"user_id": ObjectId(user_id)})
        await db.coding_solutions.delete_many({"user_id": ObjectId(user_id)})
        await db.coding_analytics.delete_many({"user_id": ObjectId(user_id)})
        
        return {
            "success": True,
            "message": "User deleted successfully"
        }
        
    except Exception as e:
        print(f"[ERROR] [ADMIN] Error deleting user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")

@router.post("/users")
async def create_user(user_data: UserCreate, user: dict = Depends(require_admin)):
    """Create a new user"""
    try:
        db = await get_db()
        
        # Check if email already exists
        existing_user = await db.users.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already exists")
        
        # Hash password
        from models.models import UserModel
        hashed_password = UserModel.hash_password(user_data.password)
        
        # Create user document
        user_doc = {
            "username": user_data.username,
            "email": user_data.email,
            "password": hashed_password,
            "role": user_data.role or "student",
            "is_admin": user_data.role == "admin",
            "name": user_data.name,
            "created_at": datetime.utcnow()
        }
        
        # Insert user
        result = await db.users.insert_one(user_doc)
        
        return {
            "success": True,
            "message": "User created successfully",
            "user_id": str(result.inserted_id)
        }
        
    except Exception as e:
        print(f"[ERROR] [ADMIN] Error creating user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")

@router.get("/content/assessments")
async def get_all_assessments(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    user: dict = Depends(require_admin)
):
    """Get all assessments for content oversight"""
    try:
        db = await get_db()
        
        # Build query
        query = {}
        if search:
            query["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"topic": {"$regex": search, "$options": "i"}}
            ]
        
        # Get total count
        total_assessments = await db.assessments.count_documents(query)
        
        # Get assessments with pagination
        skip = (page - 1) * limit
        assessments = await db.assessments.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(None)
        
        # Format assessments
        formatted_assessments = []
        for assessment in assessments:
            # Get creator info
            creator = await db.users.find_one({"_id": ObjectId(assessment["created_by"])})
            creator_name = creator.get("username", creator.get("email", "Unknown")) if creator else "Unknown"
            
            # Get completion count
            completion_count = await db.results.count_documents({"assessment_id": assessment["_id"]})
            
            formatted_assessments.append({
                "id": str(assessment["_id"]),
                "title": assessment.get("title"),
                "topic": assessment.get("topic"),
                "difficulty": assessment.get("difficulty"),
                "type": assessment.get("type", "mcq"),
                "created_by": creator_name,
                "created_at": assessment.get("created_at"),
                "completion_count": completion_count,
                "is_published": assessment.get("is_published", False)
            })
        
        return {
            "success": True,
            "assessments": formatted_assessments,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_assessments,
                "pages": (total_assessments + limit - 1) // limit
            }
        }
        
    except Exception as e:
        print(f"[ERROR] [ADMIN] Error fetching assessments: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch assessments: {str(e)}")

@router.get("/content/coding-problems")
async def get_all_coding_problems(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    user: dict = Depends(require_admin)
):
    """Get all coding problems for content oversight"""
    try:
        db = await get_db()
        
        # Build query
        query = {}
        if search:
            query["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"topic": {"$regex": search, "$options": "i"}}
            ]
        
        # Get total count
        total_problems = await db.coding_problems.count_documents(query)
        
        # Get problems with pagination
        skip = (page - 1) * limit
        problems = await db.coding_problems.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(None)
        
        # Format problems
        formatted_problems = []
        for problem in problems:
            # Get submission count
            submission_count = await db.coding_solutions.count_documents({"problem_id": problem["_id"]})
            
            formatted_problems.append({
                "id": str(problem["_id"]),
                "title": problem.get("title"),
                "topic": problem.get("topic"),
                "difficulty": problem.get("difficulty"),
                "created_by": problem.get("created_by", "AI"),
                "created_at": problem.get("created_at"),
                "submission_count": submission_count,
                "success_rate": problem.get("success_rate", 0.0),
                "average_time": problem.get("average_time")
            })
        
        return {
            "success": True,
            "problems": formatted_problems,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total_problems,
                "pages": (total_problems + limit - 1) // limit
            }
        }
        
    except Exception as e:
        print(f"[ERROR] [ADMIN] Error fetching coding problems: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch coding problems: {str(e)}")
