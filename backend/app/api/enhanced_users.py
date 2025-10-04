"""
Enhanced Users Router with AI Learning Path and Gamification
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
from pydantic import BaseModel

from ..db import get_db
from ..models.models import UserModel, LearningPathModel, BadgeModel
from .endpoints.auth import get_current_user_id
from ..services.gemini_coding_service import gemini_coding_service

router = APIRouter(prefix="/api/users", tags=["enhanced_users"])

# Response Models
class UserGamificationResponse(BaseModel):
    xp: int
    level: int
    streak: int
    longest_streak: int
    badges: List[str]
    next_level_xp: int
    progress_to_next_level: float

class LearningPathResponse(BaseModel):
    current_skill_assessment: Dict[str, Any]
    learning_objectives: List[Dict[str, Any]]
    recommended_topics: List[Dict[str, Any]]
    practice_schedule: Dict[str, Any]
    improvement_areas: List[Dict[str, Any]]
    milestone_tracking: List[Dict[str, Any]]
    ai_generated: bool
    last_updated: str

class SkillProficiencyResponse(BaseModel):
    topic: str
    proficiency_score: float
    questions_answered: int
    correct_answers: int
    average_time: float
    last_practice: str

class BadgeResponse(BaseModel):
    name: str
    description: str
    icon: str
    xp_reward: int
    category: str
    rarity: str
    earned_at: str

# Gamification Endpoints

@router.get("/{user_id}/gamification", response_model=UserGamificationResponse)
async def get_user_gamification(user_id: str, current_user_id: str = Depends(get_current_user_id)):
    """Get user's gamification data"""
    try:
        if user_id != current_user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        db = await get_db()
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Calculate next level XP (exponential growth)
        current_level = user.get("level", 1)
        next_level_xp = (current_level * 100) + ((current_level - 1) * 50)
        current_xp = user.get("xp", 0)
        previous_level_xp = ((current_level - 1) * 100) + ((current_level - 2) * 50) if current_level > 1 else 0
        progress_to_next_level = (current_xp - previous_level_xp) / (next_level_xp - previous_level_xp) if next_level_xp > previous_level_xp else 1.0
        
        return UserGamificationResponse(
            xp=current_xp,
            level=current_level,
            streak=user.get("streak", 0),
            longest_streak=user.get("longest_streak", 0),
            badges=user.get("badges", []),
            next_level_xp=next_level_xp,
            progress_to_next_level=min(progress_to_next_level, 1.0)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{user_id}/update-activity")
async def update_user_activity(user_id: str, current_user_id: str = Depends(get_current_user_id)):
    """Update user activity and streaks"""
    try:
        if user_id != current_user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        db = await get_db()
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        now = datetime.utcnow()
        last_activity = user.get("last_activity")
        
        # Calculate streak
        if last_activity:
            days_since_last_activity = (now.date() - last_activity.date()).days
            if days_since_last_activity == 1:
                # Continue streak
                new_streak = user.get("streak", 0) + 1
                new_longest_streak = max(new_streak, user.get("longest_streak", 0))
            elif days_since_last_activity == 0:
                # Same day, keep current streak
                new_streak = user.get("streak", 0)
                new_longest_streak = user.get("longest_streak", 0)
            else:
                # Streak broken
                new_streak = 1
                new_longest_streak = user.get("longest_streak", 0)
        else:
            # First activity
            new_streak = 1
            new_longest_streak = 1
        
        # Update user
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "last_activity": now,
                    "streak": new_streak,
                    "longest_streak": new_longest_streak
                }
            }
        )
        
        return {"success": True, "streak": new_streak}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{user_id}/award-xp")
async def award_xp(user_id: str, xp_amount: int, reason: str, current_user_id: str = Depends(get_current_user_id)):
    """Award XP to user"""
    try:
        if user_id != current_user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        db = await get_db()
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        current_xp = user.get("xp", 0)
        current_level = user.get("level", 1)
        new_xp = current_xp + xp_amount
        
        # Check for level up
        new_level = current_level
        while new_xp >= ((new_level * 100) + ((new_level - 1) * 50)):
            new_level += 1
        
        # Update user
        update_data = {"xp": new_xp}
        if new_level > current_level:
            update_data["level"] = new_level
        
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        
        return {
            "success": True,
            "xp_awarded": xp_amount,
            "new_xp": new_xp,
            "leveled_up": new_level > current_level,
            "new_level": new_level
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}/badges", response_model=List[BadgeResponse])
async def get_user_badges(user_id: str, current_user_id: str = Depends(get_current_user_id)):
    """Get user's badges"""
    try:
        if user_id != current_user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        db = await get_db()
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_badges = user.get("badges", [])
        badges = await db.badges.find({"name": {"$in": user_badges}}).to_list(None)
        
        badge_responses = []
        for badge in badges:
            badge_responses.append(BadgeResponse(
                name=badge["name"],
                description=badge["description"],
                icon=badge["icon"],
                xp_reward=badge["xp_reward"],
                category=badge["category"],
                rarity=badge["rarity"],
                earned_at=badge.get("earned_at", "").isoformat() if badge.get("earned_at") else ""
            ))
        
        return badge_responses
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# AI Learning Path Endpoints

@router.get("/{user_id}/learning-path", response_model=LearningPathResponse)
async def get_learning_path(user_id: str, current_user_id: str = Depends(get_current_user_id)):
    """Get AI-generated learning path for user"""
    try:
        if user_id != current_user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        db = await get_db()
        
        # Check if learning path exists
        existing_path = await db.learning_paths.find_one({"user_id": ObjectId(user_id)})
        
        if existing_path and (datetime.utcnow() - existing_path["last_updated"]).days < 7:
            # Return existing path if it's less than 7 days old
            return LearningPathResponse(
                current_skill_assessment=existing_path["current_skill_assessment"],
                learning_objectives=existing_path["learning_objectives"],
                recommended_topics=existing_path["recommended_topics"],
                practice_schedule=existing_path["practice_schedule"],
                improvement_areas=existing_path["improvement_areas"],
                milestone_tracking=existing_path["milestone_tracking"],
                ai_generated=existing_path["ai_generated"],
                last_updated=existing_path["last_updated"].isoformat()
            )
        
        # Generate new learning path using AI
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user's recent results and analytics
        results = await db.results.find({"user_id": str(user_id)}).sort("date", -1).limit(20).to_list(None)
        
        # Calculate user analytics
        total_assessments = len(results)
        total_questions = sum(r.get("total_questions", 0) for r in results)
        total_score = sum(r.get("score", 0) for r in results)
        average_score = (total_score / total_questions * 100) if total_questions > 0 else 0
        
        # Get topics and difficulties
        topics = list(set(r.get("topic", "") for r in results))
        difficulties = list(set(r.get("difficulty", "") for r in results))
        
        user_analytics = {
            "total_problems_solved": total_assessments,
            "success_rate": average_score,
            "skill_level": "beginner" if average_score < 50 else "intermediate" if average_score < 80 else "advanced",
            "strong_topics": topics[:3],  # Top 3 topics
            "weak_topics": topics[-3:] if len(topics) > 3 else [],
            "preferred_language": "python"  # Default
        }
        
        # Generate learning path using AI
        learning_path_data = await gemini_coding_service.generate_learning_path(results, user_analytics)
        
        # Save learning path
        learning_path_doc = {
            "user_id": ObjectId(user_id),
            "current_skill_assessment": learning_path_data["current_skill_assessment"],
            "learning_objectives": learning_path_data["learning_objectives"],
            "recommended_topics": learning_path_data["recommended_topics"],
            "practice_schedule": learning_path_data["practice_schedule"],
            "improvement_areas": learning_path_data["improvement_areas"],
            "milestone_tracking": learning_path_data["milestone_tracking"],
            "ai_generated": True,
            "last_updated": datetime.utcnow()
        }
        
        if existing_path:
            await db.learning_paths.update_one(
                {"user_id": ObjectId(user_id)},
                {"$set": learning_path_doc}
            )
        else:
            await db.learning_paths.insert_one(learning_path_doc)
        
        return LearningPathResponse(
            current_skill_assessment=learning_path_data["current_skill_assessment"],
            learning_objectives=learning_path_data["learning_objectives"],
            recommended_topics=learning_path_data["recommended_topics"],
            practice_schedule=learning_path_data["practice_schedule"],
            improvement_areas=learning_path_data["improvement_areas"],
            milestone_tracking=learning_path_data["milestone_tracking"],
            ai_generated=True,
            last_updated=datetime.utcnow().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}/skill-proficiency", response_model=List[SkillProficiencyResponse])
async def get_skill_proficiency(user_id: str, current_user_id: str = Depends(get_current_user_id)):
    """Get skill proficiency data for radar chart"""
    try:
        if user_id != current_user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        db = await get_db()
        
        # Get user's results grouped by topic
        pipeline = [
            {"$match": {"user_id": str(user_id)}},
            {"$group": {
                "_id": "$topic",
                "total_questions": {"$sum": "$total_questions"},
                "correct_answers": {"$sum": "$score"},
                "avg_time": {"$avg": "$time_taken"},
                "last_practice": {"$max": "$date"}
            }}
        ]
        
        topic_stats = await db.results.aggregate(pipeline).to_list(None)
        
        skill_proficiencies = []
        for stat in topic_stats:
            topic = stat["_id"]
            total_questions = stat["total_questions"]
            correct_answers = stat["correct_answers"]
            proficiency_score = (correct_answers / total_questions * 100) if total_questions > 0 else 0
            avg_time = stat["avg_time"] or 0
            last_practice = stat["last_practice"].isoformat() if isinstance(stat["last_practice"], datetime) else str(stat["last_practice"])
            
            skill_proficiencies.append(SkillProficiencyResponse(
                topic=topic,
                proficiency_score=round(proficiency_score, 2),
                questions_answered=total_questions,
                correct_answers=correct_answers,
                average_time=round(avg_time, 2),
                last_practice=last_practice
            ))
        
        return skill_proficiencies
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{user_id}/check-badges")
async def check_and_award_badges(user_id: str, current_user_id: str = Depends(get_current_user_id)):
    """Check and award new badges to user"""
    try:
        if user_id != current_user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        db = await get_db()
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get all available badges
        all_badges = await db.badges.find({}).to_list(None)
        user_badges = set(user.get("badges", []))
        new_badges = []
        
        for badge in all_badges:
            if badge["name"] not in user_badges:
                # Check if user meets criteria
                criteria = badge["criteria"]
                meets_criteria = True
                
                if "min_xp" in criteria and user.get("xp", 0) < criteria["min_xp"]:
                    meets_criteria = False
                if "min_streak" in criteria and user.get("streak", 0) < criteria["min_streak"]:
                    meets_criteria = False
                if "min_perfect_scores" in criteria and user.get("perfect_scores", 0) < criteria["min_perfect_scores"]:
                    meets_criteria = False
                if "min_questions" in criteria and user.get("total_questions_answered", 0) < criteria["min_questions"]:
                    meets_criteria = False
                
                if meets_criteria:
                    new_badges.append(badge)
        
        if new_badges:
            # Award new badges
            new_badge_names = [badge["name"] for badge in new_badges]
            total_xp_reward = sum(badge["xp_reward"] for badge in new_badges)
            
            await db.users.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$addToSet": {"badges": {"$each": new_badge_names}},
                    "$inc": {"xp": total_xp_reward}
                }
            )
        
        return {
            "success": True,
            "new_badges": [{"name": badge["name"], "description": badge["description"], "xp_reward": badge["xp_reward"]} for badge in new_badges],
            "total_xp_awarded": sum(badge["xp_reward"] for badge in new_badges)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
