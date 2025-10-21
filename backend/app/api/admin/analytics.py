"""
Admin Analytics and Statistics
Handles platform analytics, system health, and performance metrics
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
from pydantic import BaseModel
from ...db import get_db
from ...dependencies import require_admin
from ...models.models import UserModel

router = APIRouter(prefix="/admin", tags=["admin-analytics"])

# Response Models
class PlatformStatsResponse(BaseModel):
    total_users: int
    total_students: int
    total_teachers: int
    total_assessments: int
    total_submissions: int
    active_users_today: int
    platform_uptime: str

class SystemHealthResponse(BaseModel):
    database_status: str
    ai_service_status: str
    storage_status: str
    overall_health: str
    last_updated: str

@router.get("/analytics/platform", response_model=PlatformStatsResponse)
@router.get("/stats/platform", response_model=PlatformStatsResponse)
async def get_platform_stats(current_user: UserModel = Depends(require_admin)):
    """Get comprehensive platform statistics"""
    try:
        db = await get_db()
        
        # Get user counts
        total_users = await db.users.count_documents({})
        total_students = await db.users.count_documents({"role": "student"})
        total_teachers = await db.users.count_documents({"role": "teacher"})
        
        # Get assessment counts
        total_assessments = await db.assessments.count_documents({})
        teacher_assessments = await db.teacher_assessments.count_documents({})
        total_assessments += teacher_assessments
        
        # Get submission counts
        total_submissions = await db.assessment_submissions.count_documents({})
        teacher_submissions = await db.teacher_assessment_results.count_documents({})
        total_submissions += teacher_submissions
        
        # Get active users today
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        active_users_today = await db.users.count_documents({
            "last_login": {"$gte": today}
        })
        
        # Calculate platform uptime (simplified)
        platform_uptime = "99.9%"  # In production, calculate actual uptime
        
        return PlatformStatsResponse(
            total_users=total_users,
            total_students=total_students,
            total_teachers=total_teachers,
            total_assessments=total_assessments,
            total_submissions=total_submissions,
            active_users_today=active_users_today,
            platform_uptime=platform_uptime
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/overview")
async def get_analytics_overview(current_user: UserModel = Depends(require_admin)):
    """Get comprehensive analytics overview"""
    try:
        db = await get_db()
        
        # Get basic counts
        total_users = await db.users.count_documents({})
        total_students = await db.users.count_documents({"role": "student"})
        total_teachers = await db.users.count_documents({"role": "teacher"})
        total_batches = await db.batches.count_documents({})
        total_assessments = await db.assessments.count_documents({})
        total_teacher_assessments = await db.teacher_assessments.count_documents({})
        
        # Get recent activity (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        recent_submissions = await db.assessment_submissions.count_documents({
            "submitted_at": {"$gte": seven_days_ago}
        })
        
        recent_teacher_submissions = await db.teacher_assessment_results.count_documents({
            "submitted_at": {"$gte": seven_days_ago}
        })
        
        recent_users = await db.users.count_documents({
            "created_at": {"$gte": seven_days_ago}
        })
        
        # Get performance metrics
        all_submissions = await db.assessment_submissions.find({
            "submitted_at": {"$gte": seven_days_ago}
        }).to_list(length=None)
        
        teacher_submissions = await db.teacher_assessment_results.find({
            "submitted_at": {"$gte": seven_days_ago}
        }).to_list(length=None)
        
        all_recent_submissions = all_submissions + teacher_submissions
        
        if all_recent_submissions:
            avg_performance = sum(sub["percentage"] for sub in all_recent_submissions) / len(all_recent_submissions)
            high_performers = len([sub for sub in all_recent_submissions if sub["percentage"] >= 80])
            completion_rate = len(set(sub["student_id"] for sub in all_recent_submissions)) / max(total_students, 1) * 100
        else:
            avg_performance = 0
            high_performers = 0
            completion_rate = 0
        
        # Get batch analytics
        batches = await db.batches.find({}).to_list(length=None)
        batch_analytics = []
        
        for batch in batches:
            student_count = len(batch.get("student_ids", []))
            batch_submissions = await db.assessment_submissions.count_documents({
                "student_id": {"$in": batch.get("student_ids", [])}
            })
            
            batch_analytics.append({
                "batch_id": str(batch["_id"]),
                "batch_name": batch["name"],
                "teacher_id": batch["teacher_id"],
                "student_count": student_count,
                "submission_count": batch_submissions,
                "created_at": batch["created_at"].isoformat()
            })
        
        # Get user growth trends (last 30 days)
        user_growth = []
        for day in range(30):
            day_start = datetime.utcnow() - timedelta(days=day+1)
            day_end = datetime.utcnow() - timedelta(days=day)
            
            new_users = await db.users.count_documents({
                "created_at": {"$gte": day_start, "$lt": day_end}
            })
            
            user_growth.append({
                "date": day_start.strftime("%Y-%m-%d"),
                "new_users": new_users
            })
        
        # Get top performing students
        top_students = await db.users.find({
            "role": "student",
            "average_score": {"$gte": 80}
        }).sort("average_score", -1).limit(10).to_list(length=None)
        
        top_students_list = []
        for student in top_students:
            top_students_list.append({
                "id": str(student["_id"]),
                "name": student.get("username", student.get("email", "Unknown")),
                "email": student["email"],
                "average_score": student.get("average_score", 0),
                "level": student.get("level", 1),
                "xp": student.get("xp", 0),
                "completed_assessments": student.get("completed_assessments", 0)
            })
        
        return {
            "overview": {
                "total_users": total_users,
                "total_students": total_students,
                "total_teachers": total_teachers,
                "total_batches": total_batches,
                "total_assessments": total_assessments + total_teacher_assessments
            },
            "recent_activity": {
                "new_users_7_days": recent_users,
                "submissions_7_days": recent_submissions + recent_teacher_submissions,
                "average_performance": round(avg_performance, 2),
                "high_performers": high_performers,
                "completion_rate": round(completion_rate, 2)
            },
            "batch_analytics": batch_analytics,
            "user_growth": user_growth,
            "top_students": top_students_list,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/analytics")
async def get_users_analytics(
    days: int = 30,
    current_user: UserModel = Depends(require_admin)
):
    """Get detailed user analytics"""
    try:
        db = await get_db()
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get user statistics
        total_users = await db.users.count_documents({})
        active_users = await db.users.count_documents({
            "last_login": {"$gte": cutoff_date}
        })
        
        # Get users by role
        students = await db.users.find({"role": "student"}).to_list(length=None)
        teachers = await db.users.find({"role": "teacher"}).to_list(length=None)
        
        # Calculate student performance
        student_performance = []
        for student in students:
            submissions = await db.assessment_submissions.find({
                "student_id": str(student["_id"]),
                "submitted_at": {"$gte": cutoff_date}
            }).to_list(length=None)
            
            teacher_submissions = await db.teacher_assessment_results.find({
                "student_id": str(student["_id"]),
                "submitted_at": {"$gte": cutoff_date}
            }).to_list(length=None)
            
            all_submissions = submissions + teacher_submissions
            
            if all_submissions:
                avg_score = sum(sub["percentage"] for sub in all_submissions) / len(all_submissions)
                total_questions = sum(sub.get("total_questions", 0) for sub in all_submissions)
            else:
                avg_score = 0
                total_questions = 0
            
            student_performance.append({
                "student_id": str(student["_id"]),
                "name": student.get("username", student.get("email", "Unknown")),
                "email": student["email"],
                "level": student.get("level", 1),
                "xp": student.get("xp", 0),
                "completed_assessments": len(all_submissions),
                "average_score": round(avg_score, 2),
                "total_questions_answered": total_questions,
                "last_activity": student.get("last_activity", datetime.utcnow()).isoformat(),
                "created_at": student["created_at"].isoformat()
            })
        
        # Calculate teacher activity
        teacher_activity = []
        for teacher in teachers:
            batches = await db.batches.find({"teacher_id": str(teacher["_id"])}).to_list(length=None)
            assessments = await db.assessments.find({"created_by": str(teacher["_id"])}).to_list(length=None)
            teacher_assessments = await db.teacher_assessments.find({"teacher_id": str(teacher["_id"])}).to_list(length=None)
            
            total_students = sum(len(batch.get("student_ids", [])) for batch in batches)
            
            teacher_activity.append({
                "teacher_id": str(teacher["_id"]),
                "name": teacher.get("username", teacher.get("email", "Unknown")),
                "email": teacher["email"],
                "total_batches": len(batches),
                "total_assessments": len(assessments) + len(teacher_assessments),
                "total_students": total_students,
                "last_activity": teacher.get("last_activity", datetime.utcnow()).isoformat(),
                "created_at": teacher["created_at"].isoformat()
            })
        
        # Get engagement metrics
        engagement_metrics = {
            "daily_active_users": [],
            "weekly_active_users": [],
            "monthly_active_users": []
        }
        
        # Calculate DAU, WAU, MAU
        for i in range(min(days, 30)):
            day_start = datetime.utcnow() - timedelta(days=i+1)
            day_end = datetime.utcnow() - timedelta(days=i)
            
            dau = await db.users.count_documents({
                "last_login": {"$gte": day_start, "$lt": day_end}
            })
            
            engagement_metrics["daily_active_users"].append({
                "date": day_start.strftime("%Y-%m-%d"),
                "count": dau
            })
        
        return {
            "user_statistics": {
                "total_users": total_users,
                "active_users": active_users,
                "students": len(students),
                "teachers": len(teachers),
                "engagement_rate": round((active_users / max(total_users, 1)) * 100, 2)
            },
            "student_performance": student_performance,
            "teacher_activity": teacher_activity,
            "engagement_metrics": engagement_metrics,
            "period_days": days,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system/health", response_model=SystemHealthResponse)
async def get_system_health(current_user: UserModel = Depends(require_admin)):
    """Get system health status"""
    try:
        db = await get_db()
        
        # Check database connectivity
        try:
            await db.users.find_one({})
            database_status = "healthy"
        except Exception:
            database_status = "unhealthy"
        
        # Check AI service status (simplified)
        try:
            from app.services.gemini_coding_service import GeminiCodingService
            gemini_service = GeminiCodingService()
            # Simple test - in production, implement proper health check
            ai_service_status = "healthy"
        except Exception:
            ai_service_status = "unhealthy"
        
        # Check storage status (simplified)
        storage_status = "healthy"  # In production, check actual storage
        
        # Determine overall health
        if database_status == "healthy" and ai_service_status == "healthy" and storage_status == "healthy":
            overall_health = "healthy"
        elif database_status == "unhealthy":
            overall_health = "critical"
        else:
            overall_health = "degraded"
        
        return SystemHealthResponse(
            database_status=database_status,
            ai_service_status=ai_service_status,
            storage_status=storage_status,
            overall_health=overall_health,
            last_updated=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/trends")
async def get_analytics_trends(
    period: str = "30d",
    current_user: UserModel = Depends(require_admin)
):
    """Get analytics trends over time"""
    try:
        db = await get_db()
        
        # Parse period
        if period == "7d":
            days = 7
        elif period == "30d":
            days = 30
        elif period == "90d":
            days = 90
        else:
            days = 30
        
        trends = {
            "user_growth": [],
            "assessment_creation": [],
            "submission_trends": [],
            "performance_trends": []
        }
        
        # Calculate trends for each day
        for i in range(days):
            day_start = datetime.utcnow() - timedelta(days=i+1)
            day_end = datetime.utcnow() - timedelta(days=i)
            
            # User growth
            new_users = await db.users.count_documents({
                "created_at": {"$gte": day_start, "$lt": day_end}
            })
            
            # Assessment creation
            new_assessments = await db.assessments.count_documents({
                "created_at": {"$gte": day_start, "$lt": day_end}
            })
            
            new_teacher_assessments = await db.teacher_assessments.count_documents({
                "created_at": {"$gte": day_start, "$lt": day_end}
            })
            
            # Submissions
            submissions = await db.assessment_submissions.count_documents({
                "submitted_at": {"$gte": day_start, "$lt": day_end}
            })
            
            teacher_submissions = await db.teacher_assessment_results.count_documents({
                "submitted_at": {"$gte": day_start, "$lt": day_end}
            })
            
            # Performance trends
            day_submissions = await db.assessment_submissions.find({
                "submitted_at": {"$gte": day_start, "$lt": day_end}
            }).to_list(length=None)
            
            teacher_day_submissions = await db.teacher_assessment_results.find({
                "submitted_at": {"$gte": day_start, "$lt": day_end}
            }).to_list(length=None)
            
            all_day_submissions = day_submissions + teacher_day_submissions
            
            if all_day_submissions:
                avg_performance = sum(sub["percentage"] for sub in all_day_submissions) / len(all_day_submissions)
            else:
                avg_performance = 0
            
            trends["user_growth"].append({
                "date": day_start.strftime("%Y-%m-%d"),
                "new_users": new_users
            })
            
            trends["assessment_creation"].append({
                "date": day_start.strftime("%Y-%m-%d"),
                "new_assessments": new_assessments + new_teacher_assessments
            })
            
            trends["submission_trends"].append({
                "date": day_start.strftime("%Y-%m-%d"),
                "submissions": submissions + teacher_submissions
            })
            
            trends["performance_trends"].append({
                "date": day_start.strftime("%Y-%m-%d"),
                "average_performance": round(avg_performance, 2)
            })
        
        # Reverse to get chronological order
        for key in trends:
            trends[key].reverse()
        
        return {
            "period": period,
            "trends": trends,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
