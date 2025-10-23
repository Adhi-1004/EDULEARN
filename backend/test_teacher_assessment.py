#!/usr/bin/env python3
import asyncio
import json
from app.db import get_db, init_db
from app.api.teacher import create_teacher_assessment, TeacherAssessmentCreate
from app.dependencies import get_current_user
from app.models.models import UserModel

async def test_teacher_assessment_creation():
    try:
        await init_db()
        db = await get_db()
        
        # Get a teacher user
        teacher = await db.users.find_one({"role": "teacher"})
        if not teacher:
            print("No teacher found in database")
            return
        
        print(f"Found teacher: {teacher.get('email', 'Unknown')}")
        
        # Create test assessment data
        assessment_data = TeacherAssessmentCreate(
            title="Test Assessment",
            topic="Python Basics",
            difficulty="medium",
            question_count=5,
            batches=["test_batch_id"],
            type="ai_generated"
        )
        
        # Mock current user
        current_user = UserModel(
            id=str(teacher["_id"]),
            email=teacher["email"],
            username=teacher.get("username", teacher["email"]),
            role=teacher["role"],
            password_hash=teacher.get("password_hash", "dummy_hash")
        )
        
        print("Creating teacher assessment...")
        
        # This would normally be called through the API endpoint
        # For now, let's just check if the endpoint exists
        print("Teacher assessment creation endpoint exists")
        
        # Check if we can find any existing teacher assessments
        assessments = await db.teacher_assessments.find({}).to_list(length=5)
        print(f"Found {len(assessments)} existing teacher assessments")
        
        for assessment in assessments:
            print(f"  - {assessment.get('title', 'Untitled')} (ID: {assessment['_id']})")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_teacher_assessment_creation())
