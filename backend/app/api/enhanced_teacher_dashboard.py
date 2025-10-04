"""
Enhanced Teacher Dashboard Router with AI Features
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
from pydantic import BaseModel

from database import get_db
from models.models import BatchModel, BatchAnalyticsModel, AIStudentReportModel, TeacherPerformanceModel
from routers.teacher_dashboard import get_current_user
from services.gemini_coding_service import gemini_coding_service

router = APIRouter(prefix="/api/teacher", tags=["enhanced_teacher_dashboard"])

# Response Models
class BatchMissionControlResponse(BaseModel):
    batch_id: str
    batch_name: str
    total_students: int
    average_score: float
    completion_rate: float
    struggling_students: List[Dict[str, Any]]
    top_performers: List[Dict[str, Any]]
    recent_activities: List[Dict[str, Any]]
    health_score: float

class AIStudentReportResponse(BaseModel):
    student_id: str
    student_name: str
    report_content: str
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    performance_summary: Dict[str, Any]
    generated_at: str

class SmartAssessmentRequest(BaseModel):
    title: str
    topic: str
    difficulty: str
    question_count: int
    batch_ids: List[str]
    adapt_to_weaknesses: bool = True

class TeacherPerformanceResponse(BaseModel):
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

# Batch Mission Control Endpoints

@router.get("/batches/mission-control", response_model=List[BatchMissionControlResponse])
async def get_batch_mission_control(teacher: dict = Depends(get_current_user)):
    """Get batch performance mission control data"""
    try:
        db = await get_db()
        
        # Get all batches for this teacher
        batches = await db.batches.find({"teacher_id": str(teacher["_id"])}).to_list(None)
        mission_control_data = []
        
        for batch in batches:
            batch_id = str(batch["_id"])
            student_ids = batch.get("student_ids", [])
            
            if not student_ids:
                # Empty batch
                mission_control_data.append(BatchMissionControlResponse(
                    batch_id=batch_id,
                    batch_name=batch["name"],
                    total_students=0,
                    average_score=0.0,
                    completion_rate=0.0,
                    struggling_students=[],
                    top_performers=[],
                    recent_activities=[],
                    health_score=0.0
                ))
                continue
            
            # Get student results for this batch
            results = await db.results.find({"user_id": {"$in": student_ids}}).to_list(None)
            
            if not results:
                mission_control_data.append(BatchMissionControlResponse(
                    batch_id=batch_id,
                    batch_name=batch["name"],
                    total_students=len(student_ids),
                    average_score=0.0,
                    completion_rate=0.0,
                    struggling_students=[],
                    top_performers=[],
                    recent_activities=[],
                    health_score=0.0
                ))
                continue
            
            # Calculate batch metrics
            total_students = len(student_ids)
            total_score = sum(r.get("score", 0) for r in results)
            total_questions = sum(r.get("total_questions", 0) for r in results)
            average_score = (total_score / total_questions * 100) if total_questions > 0 else 0
            
            # Calculate completion rate
            unique_students_with_results = len(set(r["user_id"] for r in results))
            completion_rate = (unique_students_with_results / total_students * 100) if total_students > 0 else 0
            
            # Get struggling students (bottom 3 performers)
            student_scores = {}
            for result in results:
                student_id = result["user_id"]
                if student_id not in student_scores:
                    student_scores[student_id] = {"total_score": 0, "total_questions": 0}
                student_scores[student_id]["total_score"] += result.get("score", 0)
                student_scores[student_id]["total_questions"] += result.get("total_questions", 0)
            
            # Calculate average scores per student
            student_averages = []
            for student_id, scores in student_scores.items():
                avg_score = (scores["total_score"] / scores["total_questions"] * 100) if scores["total_questions"] > 0 else 0
                student_averages.append({"student_id": student_id, "average_score": avg_score})
            
            # Sort by average score
            student_averages.sort(key=lambda x: x["average_score"])
            
            # Get struggling students (bottom 3)
            struggling_students = []
            for student_data in student_averages[:3]:
                student = await db.users.find_one({"_id": ObjectId(student_data["student_id"])})
                if student:
                    struggling_students.append({
                        "student_id": student_data["student_id"],
                        "student_name": student.get("name", "Unknown"),
                        "average_score": round(student_data["average_score"], 2),
                        "issues": ["Low performance", "Needs attention"]
                    })
            
            # Get top performers (top 3)
            top_performers = []
            for student_data in student_averages[-3:]:
                student = await db.users.find_one({"_id": ObjectId(student_data["student_id"])})
                if student:
                    top_performers.append({
                        "student_id": student_data["student_id"],
                        "student_name": student.get("name", "Unknown"),
                        "average_score": round(student_data["average_score"], 2),
                        "achievements": ["High performance", "Excellent work"]
                    })
            
            # Get recent activities
            recent_activities = []
            for result in results[-5:]:  # Last 5 results
                student = await db.users.find_one({"_id": ObjectId(result["user_id"])})
                recent_activities.append({
                    "student_name": student.get("name", "Unknown") if student else "Unknown",
                    "topic": result.get("topic", ""),
                    "score": result.get("score", 0),
                    "total_questions": result.get("total_questions", 0),
                    "date": result.get("date", "").isoformat() if isinstance(result.get("date"), datetime) else str(result.get("date", ""))
                })
            
            # Calculate health score (0-100)
            health_score = (average_score * 0.4 + completion_rate * 0.3 + (100 - len(struggling_students) * 10)) / 100
            health_score = max(0, min(100, health_score))
            
            mission_control_data.append(BatchMissionControlResponse(
                batch_id=batch_id,
                batch_name=batch["name"],
                total_students=total_students,
                average_score=round(average_score, 2),
                completion_rate=round(completion_rate, 2),
                struggling_students=struggling_students,
                top_performers=top_performers,
                recent_activities=recent_activities,
                health_score=round(health_score, 2)
            ))
        
        return mission_control_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# AI Student Reports Endpoints

@router.post("/students/{student_id}/ai-report", response_model=AIStudentReportResponse)
async def generate_ai_student_report(student_id: str, teacher: dict = Depends(get_current_user)):
    """Generate AI-powered student performance report"""
    try:
        db = await get_db()
        
        # Check if student exists
        student = await db.users.find_one({"_id": ObjectId(student_id), "role": "student"})
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Get student's performance data
        results = await db.results.find({"user_id": student_id}).sort("date", -1).to_list(None)
        
        if not results:
            raise HTTPException(status_code=400, detail="No performance data available for this student")
        
        # Calculate performance metrics
        total_assessments = len(results)
        total_questions = sum(r.get("total_questions", 0) for r in results)
        total_score = sum(r.get("score", 0) for r in results)
        average_score = (total_score / total_questions * 100) if total_questions > 0 else 0
        
        # Get topic performance
        topic_performance = {}
        for result in results:
            topic = result.get("topic", "Unknown")
            if topic not in topic_performance:
                topic_performance[topic] = {"total_score": 0, "total_questions": 0, "count": 0}
            topic_performance[topic]["total_score"] += result.get("score", 0)
            topic_performance[topic]["total_questions"] += result.get("total_questions", 0)
            topic_performance[topic]["count"] += 1
        
        # Calculate topic averages
        topic_averages = {}
        for topic, data in topic_performance.items():
            avg_score = (data["total_score"] / data["total_questions"] * 100) if data["total_questions"] > 0 else 0
            topic_averages[topic] = round(avg_score, 2)
        
        # Prepare data for AI analysis
        performance_data = {
            "student_name": student.get("name", "Unknown"),
            "total_assessments": total_assessments,
            "average_score": round(average_score, 2),
            "topic_performance": topic_averages,
            "recent_results": results[:10]  # Last 10 results
        }
        
        # Generate AI report using Gemini
        ai_report = await gemini_coding_service.generate_student_report(performance_data)
        
        # Save AI report
        report_doc = {
            "student_id": ObjectId(student_id),
            "teacher_id": ObjectId(teacher["_id"]),
            "report_content": ai_report["report_content"],
            "strengths": ai_report["strengths"],
            "weaknesses": ai_report["weaknesses"],
            "recommendations": ai_report["recommendations"],
            "performance_summary": ai_report["performance_summary"],
            "generated_at": datetime.utcnow()
        }
        
        await db.ai_student_reports.insert_one(report_doc)
        
        return AIStudentReportResponse(
            student_id=student_id,
            student_name=student.get("name", "Unknown"),
            report_content=ai_report["report_content"],
            strengths=ai_report["strengths"],
            weaknesses=ai_report["weaknesses"],
            recommendations=ai_report["recommendations"],
            performance_summary=ai_report["performance_summary"],
            generated_at=datetime.utcnow().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/students/{student_id}/ai-reports", response_model=List[AIStudentReportResponse])
async def get_student_ai_reports(student_id: str, teacher: dict = Depends(get_current_user)):
    """Get all AI reports for a student"""
    try:
        db = await get_db()
        
        # Get all AI reports for this student
        reports = await db.ai_student_reports.find({
            "student_id": ObjectId(student_id),
            "teacher_id": ObjectId(teacher["_id"])
        }).sort("generated_at", -1).to_list(None)
        
        report_responses = []
        for report in reports:
            student = await db.users.find_one({"_id": ObjectId(student_id)})
            report_responses.append(AIStudentReportResponse(
                student_id=student_id,
                student_name=student.get("name", "Unknown") if student else "Unknown",
                report_content=report["report_content"],
                strengths=report["strengths"],
                weaknesses=report["weaknesses"],
                recommendations=report["recommendations"],
                performance_summary=report["performance_summary"],
                generated_at=report["generated_at"].isoformat()
            ))
        
        return report_responses
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Smart Assessment Creator Endpoints

@router.post("/assessments/smart-create")
async def create_smart_assessment(request: SmartAssessmentRequest, teacher: dict = Depends(get_current_user)):
    """Create AI-powered assessment targeting batch weaknesses"""
    try:
        db = await get_db()
        
        if not request.batch_ids:
            raise HTTPException(status_code=400, detail="At least one batch must be specified")
        
        # Get batch data and student performance
        batch_weaknesses = {}
        all_student_ids = []
        
        for batch_id in request.batch_ids:
            batch = await db.batches.find_one({"_id": ObjectId(batch_id), "teacher_id": str(teacher["_id"])})
            if not batch:
                raise HTTPException(status_code=404, detail=f"Batch {batch_id} not found")
            
            student_ids = batch.get("student_ids", [])
            all_student_ids.extend(student_ids)
            
            if request.adapt_to_weaknesses and student_ids:
                # Analyze batch weaknesses
                results = await db.results.find({"user_id": {"$in": student_ids}}).to_list(None)
                
                # Calculate topic performance
                topic_performance = {}
                for result in results:
                    topic = result.get("topic", "Unknown")
                    if topic not in topic_performance:
                        topic_performance[topic] = {"total_score": 0, "total_questions": 0}
                    topic_performance[topic]["total_score"] += result.get("score", 0)
                    topic_performance[topic]["total_questions"] += result.get("total_questions", 0)
                
                # Find weak topics
                weak_topics = []
                for topic, data in topic_performance.items():
                    avg_score = (data["total_score"] / data["total_questions"] * 100) if data["total_questions"] > 0 else 0
                    if avg_score < 70:  # Below 70% is considered weak
                        weak_topics.append(topic)
                
                batch_weaknesses[batch_id] = {
                    "batch_name": batch["name"],
                    "weak_topics": weak_topics,
                    "student_count": len(student_ids)
                }
        
        # Generate AI assessment
        assessment_data = {
            "title": request.title,
            "topic": request.topic,
            "difficulty": request.difficulty,
            "question_count": request.question_count,
            "batch_weaknesses": batch_weaknesses,
            "adapt_to_weaknesses": request.adapt_to_weaknesses
        }
        
        ai_assessment = await gemini_coding_service.generate_smart_assessment(assessment_data)
        
        # Create assessment document
        assessment_doc = {
            "title": request.title,
            "topic": request.topic,
            "difficulty": request.difficulty,
            "question_count": request.question_count,
            "description": ai_assessment.get("description", ""),
            "created_by": str(teacher["_id"]),
            "created_at": datetime.utcnow(),
            "assigned_to": request.batch_ids,
            "ai_generated": True,
            "targeted_weaknesses": batch_weaknesses,
            "questions": ai_assessment.get("questions", [])
        }
        
        result = await db.assessments.insert_one(assessment_doc)
        
        return {
            "success": True,
            "assessment_id": str(result.inserted_id),
            "message": f"Smart assessment created with {len(ai_assessment.get('questions', []))} AI-generated questions",
            "targeted_weaknesses": batch_weaknesses,
            "ai_insights": ai_assessment.get("insights", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Teacher Performance Endpoints

@router.get("/performance/leaderboard", response_model=List[TeacherPerformanceResponse])
async def get_teacher_performance_leaderboard(teacher: dict = Depends(get_current_user)):
    """Get teacher performance leaderboard"""
    try:
        db = await get_db()
        
        # Get all teachers
        teachers = await db.users.find({"role": "teacher"}).to_list(None)
        teacher_performances = []
        
        for teacher_data in teachers:
            teacher_id = str(teacher_data["_id"])
            
            # Get teacher's batches
            batches = await db.batches.find({"teacher_id": teacher_id}).to_list(None)
            batch_ids = [str(batch["_id"]) for batch in batches]
            
            # Get all students in teacher's batches
            all_student_ids = []
            for batch in batches:
                all_student_ids.extend(batch.get("student_ids", []))
            
            if not all_student_ids:
                continue
            
            # Calculate teacher performance metrics
            student_results = await db.results.find({"user_id": {"$in": all_student_ids}}).to_list(None)
            
            if not student_results:
                continue
            
            # Calculate metrics
            total_assessments_created = await db.assessments.count_documents({"created_by": teacher_id})
            total_questions_created = await db.questions.count_documents({"created_by": teacher_id})
            
            # Student performance score
            total_score = sum(r.get("score", 0) for r in student_results)
            total_questions = sum(r.get("total_questions", 0) for r in student_results)
            average_student_score = (total_score / total_questions * 100) if total_questions > 0 else 0
            
            # Content contribution score
            content_contribution_score = min(100, (total_assessments_created * 10 + total_questions_created * 2))
            
            # Engagement score (based on student activity)
            unique_students = len(set(r["user_id"] for r in student_results))
            engagement_score = min(100, unique_students * 5)
            
            # Overall performance score
            overall_score = (average_student_score * 0.4 + content_contribution_score * 0.3 + engagement_score * 0.3)
            
            teacher_performances.append(TeacherPerformanceResponse(
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
        
        return teacher_performances[:20]  # Top 20 teachers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
