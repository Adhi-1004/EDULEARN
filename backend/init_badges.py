"""
Initialize default badges in the database
"""
import asyncio
from database import get_db
from datetime import datetime

async def init_badges():
    """Initialize default badges"""
    db = await get_db()
    
    # Check if badges already exist
    existing_badges = await db.badges.count_documents({})
    if existing_badges > 0:
        print(f"Badges already exist ({existing_badges} badges found). Skipping initialization.")
        return
    
    # Default badges
    badges = [
        {
            "name": "First Steps",
            "description": "Complete your first assessment",
            "icon": "🎯",
            "xp_reward": 50,
            "criteria": {"min_questions": 1},
            "category": "achievement",
            "rarity": "common",
            "created_at": datetime.utcnow()
        },
        {
            "name": "Perfect Score",
            "description": "Get a perfect score on an assessment",
            "icon": "💯",
            "xp_reward": 100,
            "criteria": {"min_perfect_scores": 1},
            "category": "performance",
            "rarity": "rare",
            "created_at": datetime.utcnow()
        },
        {
            "name": "Streak Master",
            "description": "Maintain a 7-day streak",
            "icon": "🔥",
            "xp_reward": 200,
            "criteria": {"min_streak": 7},
            "category": "streak",
            "rarity": "epic",
            "created_at": datetime.utcnow()
        },
        {
            "name": "Python Pro",
            "description": "Solve 10 Python coding problems",
            "icon": "🐍",
            "xp_reward": 300,
            "criteria": {"min_questions": 10, "language": "python"},
            "category": "achievement",
            "rarity": "epic",
            "created_at": datetime.utcnow()
        },
        {
            "name": "Algorithm Expert",
            "description": "Solve 20 algorithm problems",
            "icon": "🧠",
            "xp_reward": 500,
            "criteria": {"min_questions": 20, "topic": "algorithms"},
            "category": "achievement",
            "rarity": "legendary",
            "created_at": datetime.utcnow()
        },
        {
            "name": "Quick Learner",
            "description": "Answer 50 questions correctly",
            "icon": "⚡",
            "xp_reward": 250,
            "criteria": {"min_questions": 50},
            "category": "achievement",
            "rarity": "rare",
            "created_at": datetime.utcnow()
        },
        {
            "name": "Consistent Performer",
            "description": "Maintain 80% accuracy over 20 questions",
            "icon": "🎯",
            "xp_reward": 400,
            "criteria": {"min_questions": 20, "min_accuracy": 80},
            "category": "performance",
            "rarity": "epic",
            "created_at": datetime.utcnow()
        },
        {
            "name": "Daily Champion",
            "description": "Complete assessments for 30 consecutive days",
            "icon": "👑",
            "xp_reward": 1000,
            "criteria": {"min_streak": 30},
            "category": "streak",
            "rarity": "legendary",
            "created_at": datetime.utcnow()
        },
        {
            "name": "Problem Solver",
            "description": "Solve your first coding problem",
            "icon": "💻",
            "xp_reward": 100,
            "criteria": {"min_coding_solutions": 1},
            "category": "achievement",
            "rarity": "common",
            "created_at": datetime.utcnow()
        },
        {
            "name": "Code Master",
            "description": "Solve 50 coding problems",
            "icon": "🏆",
            "xp_reward": 800,
            "criteria": {"min_coding_solutions": 50},
            "category": "achievement",
            "rarity": "legendary",
            "created_at": datetime.utcnow()
        }
    ]
    
    # Insert badges
    result = await db.badges.insert_many(badges)
    print(f"Successfully created {len(result.inserted_ids)} badges")
    
    # Print created badges
    for badge in badges:
        print(f"[OK] {badge['icon']} {badge['name']} - {badge['description']}")

if __name__ == "__main__":
    asyncio.run(init_badges())
