"""
Enhanced Admin Dashboard Router with Platform Metrics and Content Oversight
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
from pydantic import BaseModel

from database import get_db
from models.models import PlatformMetricsModel, ContentQualityModel, TeacherPerformanceModel
from routers.admin_dashboard import get_current_admin
from services.gemini_coding_service import gemini_coding_service

router = APIRouter(prefix="/api/admin", tags=["enhanced_admin_dashboard"])

# Response Models
class PlatformHealthResponse(BaseModel):
    daily_active_users: int
    monthly_active_users: int
    user_engagement_ratio: float
    assessment_completion_rate: float
    feature_adoption: Dict[str, Any]
    content_quality_score: float
    system_health_score: float
    growth_metrics: Dict[str, Any]

class ContentQualityResponse(BaseModel):
    content_id: str
    content_type: str
    title: str
    success_rate: float
    failure_rate: float
    flagged_reason: Optional[str]
    ai_audit_score: Optional[float]
    ai_audit_feedback: Optional[str]
    last_audited: str
    priority: str  # "high", "medium", "low"

class ContentAuditResponse(BaseModel):
    content_id: str
    content_type: str
    title: str
    audit_score: float
    audit_feedback: str
    recommendations: List[str]
    quality_issues: List[str]
    strengths: List[str]
    audited_at: str

class TeacherLeaderboardResponse(BaseModel):
    teacher_id: str
    teacher_name: str
    student_performance_score: float
    content_contribution_score: float
    engagement_score: float
    total_assessments_created: int
    total_questions_created: int
    average_student_score: float
    student_satisfaction_score: float
    rank: int

# Platform Health & Engagement Metrics

@router.get("/metrics/platform-health", response_model=PlatformHealthResponse)
async def get_platform_health_metrics(admin: dict = Depends(get_current_admin)):
    """Get comprehensive platform health and engagement metrics"""
    try:
        db = await get_db()
        
        # Calculate date ranges
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday = today - timedelta(days=1)
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Daily Active Users (DAU)
        daily_active_users = await db.results.count_documents({"date": {"$gte": today}})
        
        # Monthly Active Users (MAU)
        monthly_active_users = await db.results.count_documents({"date": {"$gte": month_ago}})
        
        # User Engagement Ratio (DAU/MAU)
        user_engagement_ratio = (daily_active_users / monthly_active_users * 100) if monthly_active_users > 0 else 0
        
        # Assessment Completion Rate
        total_assessments_started = await db.results.count_documents({})
        total_assessments_completed = await db.results.count_documents({"score": {"$gt": 0}})
        assessment_completion_rate = (total_assessments_completed / total_assessments_started * 100) if total_assessments_started > 0 else 0
        
        # Feature Adoption Analysis
        feature_adoption = {
            "mcq_assessments": await db.results.count_documents({"type": "mcq"}),
            "coding_challenges": await db.results.count_documents({"type": "coding"}),
            "ai_generated_content": await db.assessments.count_documents({"ai_generated": True}),
            "face_recognition_users": await db.users.count_documents({"face_descriptor": {"$exists": True, "$ne": None}}),
            "gamification_users": await db.users.count_documents({"xp": {"$gt": 0}})
        }
        
        # Content Quality Score
        content_quality_entries = await db.content_quality.find({}).to_list(None)
        if content_quality_entries:
            avg_quality_score = sum(entry.get("ai_audit_score", 0) for entry in content_quality_entries if entry.get("ai_audit_score")) / len([e for e in content_quality_entries if e.get("ai_audit_score")])
        else:
            avg_quality_score = 75.0  # Default score
        
        # System Health Score
        system_health_score = min(100, (
            user_engagement_ratio * 0.3 +
            assessment_completion_rate * 0.3 +
            avg_quality_score * 0.2 +
            (100 - len([e for e in content_quality_entries if e.get("flagged_reason")]) * 2) * 0.2
        ))
        
        # Growth Metrics
        users_this_week = await db.users.count_documents({"created_at": {"$gte": week_ago}})
        users_last_week = await db.users.count_documents({
            "created_at": {"$gte": week_ago - timedelta(days=7), "$lt": week_ago}
        })
        user_growth_rate = ((users_this_week - users_last_week) / users_last_week * 100) if users_last_week > 0 else 0
        
        assessments_this_week = await db.results.count_documents({"date": {"$gte": week_ago}})
        assessments_last_week = await db.results.count_documents({
            "date": {"$gte": week_ago - timedelta(days=7), "$lt": week_ago}
        })
        assessment_growth_rate = ((assessments_this_week - assessments_last_week) / assessments_last_week * 100) if assessments_last_week > 0 else 0
        
        growth_metrics = {
            "user_growth_rate": round(user_growth_rate, 2),
            "assessment_growth_rate": round(assessment_growth_rate, 2),
            "new_users_this_week": users_this_week,
            "new_assessments_this_week": assessments_this_week
        }
        
        return PlatformHealthResponse(
            daily_active_users=daily_active_users,
            monthly_active_users=monthly_active_users,
            user_engagement_ratio=round(user_engagement_ratio, 2),
            assessment_completion_rate=round(assessment_completion_rate, 2),
            feature_adoption=feature_adoption,
            content_quality_score=round(avg_quality_score, 2),
            system_health_score=round(system_health_score, 2),
            growth_metrics=growth_metrics
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Content Quality Oversight

@router.get("/content/quality-issues", response_model=List[ContentQualityResponse])
async def get_content_quality_issues(admin: dict = Depends(get_current_admin)):
    """Get flagged content with quality issues"""
    try:
        db = await get_db()
        
        # Get flagged content
        flagged_content = await db.content_quality.find({
            "flagged_reason": {"$exists": True, "$ne": None}
        }).sort("last_audited", -1).to_list(None)
        
        quality_issues = []
        for content in flagged_content:
            # Get content details
            content_id = content["content_id"]
            content_type = content["content_type"]
            
            if content_type == "question":
                content_doc = await db.questions.find_one({"_id": ObjectId(content_id)})
                title = content_doc.get("question", "Unknown Question") if content_doc else "Unknown"
            else:
                content_doc = await db.coding_problems.find_one({"_id": ObjectId(content_id)})
                title = content_doc.get("title", "Unknown Problem") if content_doc else "Unknown"
            
            # Determine priority
            priority = "high" if content["success_rate"] < 30 or content["failure_rate"] > 70 else "medium" if content["success_rate"] < 50 else "low"
            
            quality_issues.append(ContentQualityResponse(
                content_id=content_id,
                content_type=content_type,
                title=title[:100] + "..." if len(title) > 100 else title,
                success_rate=content["success_rate"],
                failure_rate=content["failure_rate"],
                flagged_reason=content.get("flagged_reason"),
                ai_audit_score=content.get("ai_audit_score"),
                ai_audit_feedback=content.get("ai_audit_feedback"),
                last_audited=content["last_audited"].isoformat(),
                priority=priority
            ))
        
        return quality_issues
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/content/{content_id}/audit", response_model=ContentAuditResponse)
async def audit_content_with_ai(content_id: str, content_type: str, admin: dict = Depends(get_current_admin)):
    """Audit content using AI for quality assessment"""
    try:
        db = await get_db()
        
        # Get content
        if content_type == "question":
            content_doc = await db.questions.find_one({"_id": ObjectId(content_id)})
            content_text = content_doc.get("question", "") if content_doc else ""
            content_title = content_text[:50] + "..." if len(content_text) > 50 else content_text
        else:
            content_doc = await db.coding_problems.find_one({"_id": ObjectId(content_id)})
            content_text = content_doc.get("description", "") if content_doc else ""
            content_title = content_doc.get("title", "Unknown") if content_doc else "Unknown"
        
        if not content_doc:
            raise HTTPException(status_code=404, detail="Content not found")
        
        # Get content performance data
        results = await db.results.find({"content_id": content_id}).to_list(None)
        success_rate = 0
        if results:
            total_attempts = len(results)
            successful_attempts = len([r for r in results if r.get("score", 0) > 0])
            success_rate = (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0
        
        # Generate AI audit using Gemini
        audit_data = {
            "content_type": content_type,
            "content_text": content_text,
            "success_rate": success_rate,
            "total_attempts": len(results)
        }
        
        ai_audit = await gemini_coding_service.audit_content_quality(audit_data)
        
        # Update content quality record
        quality_doc = {
            "content_id": content_id,
            "content_type": content_type,
            "success_rate": success_rate,
            "failure_rate": 100 - success_rate,
            "ai_audit_score": ai_audit["audit_score"],
            "ai_audit_feedback": ai_audit["audit_feedback"],
            "last_audited": datetime.utcnow()
        }
        
        # Update or create quality record
        await db.content_quality.update_one(
            {"content_id": content_id, "content_type": content_type},
            {"$set": quality_doc},
            upsert=True
        )
        
        return ContentAuditResponse(
            content_id=content_id,
            content_type=content_type,
            title=content_title,
            audit_score=ai_audit["audit_score"],
            audit_feedback=ai_audit["audit_feedback"],
            recommendations=ai_audit["recommendations"],
            quality_issues=ai_audit["quality_issues"],
            strengths=ai_audit["strengths"],
            audited_at=datetime.utcnow().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/content/bulk-audit")
async def bulk_audit_content(admin: dict = Depends(get_current_admin)):
    """Bulk audit content for quality issues"""
    try:
        db = await get_db()
        
        # Get content that needs auditing (no recent audit or flagged)
        content_to_audit = await db.content_quality.find({
            "$or": [
                {"last_audited": {"$lt": datetime.utcnow() - timedelta(days=30)}},
                {"flagged_reason": {"$exists": True}}
            ]
        }).limit(50).to_list(None)
        
        audit_results = []
        for content in content_to_audit:
            try:
                # Perform AI audit
                audit_data = {
                    "content_type": content["content_type"],
                    "success_rate": content["success_rate"],
                    "failure_rate": content["failure_rate"]
                }
                
                ai_audit = await gemini_coding_service.audit_content_quality(audit_data)
                
                # Update quality record
                await db.content_quality.update_one(
                    {"_id": content["_id"]},
                    {
                        "$set": {
                            "ai_audit_score": ai_audit["audit_score"],
                            "ai_audit_feedback": ai_audit["audit_feedback"],
                            "last_audited": datetime.utcnow()
                        }
                    }
                )
                
                audit_results.append({
                    "content_id": content["content_id"],
                    "audit_score": ai_audit["audit_score"],
                    "flagged": ai_audit["audit_score"] < 60
                })
                
            except Exception as e:
                print(f"Error auditing content {content['content_id']}: {str(e)}")
                continue
        
        return {
            "success": True,
            "audited_count": len(audit_results),
            "results": audit_results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Teacher Performance Leaderboard

@router.get("/teachers/leaderboard", response_model=List[TeacherLeaderboardResponse])
async def get_teacher_performance_leaderboard(admin: dict = Depends(get_current_admin)):
    """Get teacher performance and contribution leaderboard"""
    try:
        db = await get_db()
        
        # Get all teachers
        teachers = await db.users.find({"role": "teacher"}).to_list(None)
        teacher_performances = []
        
        for teacher_data in teachers:
            teacher_id = str(teacher_data["_id"])
            
            # Get teacher's batches and students
            batches = await db.batches.find({"teacher_id": teacher_id}).to_list(None)
            all_student_ids = []
            for batch in batches:
                all_student_ids.extend(batch.get("student_ids", []))
            
            if not all_student_ids:
                continue
            
            # Get student results
            student_results = await db.results.find({"user_id": {"$in": all_student_ids}}).to_list(None)
            
            if not student_results:
                continue
            
            # Calculate performance metrics
            total_assessments_created = await db.assessments.count_documents({"created_by": teacher_id})
            total_questions_created = await db.questions.count_documents({"created_by": teacher_id})
            
            # Student performance score
            total_score = sum(r.get("score", 0) for r in student_results)
            total_questions = sum(r.get("total_questions", 0) for r in student_results)
            average_student_score = (total_score / total_questions * 100) if total_questions > 0 else 0
            
            # Content contribution score
            content_contribution_score = min(100, (total_assessments_created * 10 + total_questions_created * 2))
            
            # Engagement score
            unique_students = len(set(r["user_id"] for r in student_results))
            engagement_score = min(100, unique_students * 5)
            
            # Overall performance score
            overall_score = (average_student_score * 0.4 + content_contribution_score * 0.3 + engagement_score * 0.3)
            
            teacher_performances.append(TeacherLeaderboardResponse(
                teacher_id=teacher_id,
                teacher_name=teacher_data.get("name", "Unknown"),
                student_performance_score=round(average_student_score, 2),
                content_contribution_score=round(content_contribution_score, 2),
                engagement_score=round(engagement_score, 2),
                total_assessments_created=total_assessments_created,
                total_questions_created=total_questions_created,
                average_student_score=round(average_student_score, 2),
                student_satisfaction_score=round(overall_score, 2),
                rank=0  # Will be set after sorting
            ))
        
        # Sort by overall performance
        teacher_performances.sort(key=lambda x: x.student_satisfaction_score, reverse=True)
        
        # Set ranks
        for i, teacher_perf in enumerate(teacher_performances):
            teacher_perf.rank = i + 1
        
        return teacher_performances[:50]  # Top 50 teachers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# System Health Monitoring

@router.get("/system/health-detailed")
async def get_detailed_system_health(admin: dict = Depends(get_current_admin)):
    """Get detailed system health metrics"""
    try:
        db = await get_db()
        
        # Database health
        db_status = "healthy"
        try:
            await db.command("ping")
        except Exception:
            db_status = "unhealthy"
        
        # API response times (mock data)
        api_response_times = {
            "auth": 120,  # ms
            "assessments": 250,
            "results": 180,
            "users": 95
        }
        
        # Error rates (mock data)
        error_rates = {
            "4xx_errors": 2.1,  # %
            "5xx_errors": 0.3,
            "timeout_errors": 0.1
        }
        
        # Resource usage (mock data)
        resource_usage = {
            "cpu_usage": 45.2,  # %
            "memory_usage": 67.8,
            "disk_usage": 23.1,
            "network_io": 12.5
        }
        
        # User activity patterns
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        hourly_activity = []
        for hour in range(24):
            hour_start = today + timedelta(hours=hour)
            hour_end = hour_start + timedelta(hours=1)
            activity_count = await db.results.count_documents({
                "date": {"$gte": hour_start, "$lt": hour_end}
            })
            hourly_activity.append({
                "hour": hour,
                "activity_count": activity_count
            })
        
        return {
            "status": "healthy" if db_status == "healthy" else "degraded",
            "database": db_status,
            "api_response_times": api_response_times,
            "error_rates": error_rates,
            "resource_usage": resource_usage,
            "hourly_activity": hourly_activity,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
