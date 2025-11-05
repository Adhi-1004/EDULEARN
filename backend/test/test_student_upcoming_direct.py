#!/usr/bin/env python3
"""
Direct test of the student upcoming endpoint function
"""
import asyncio
from app.db import get_db, init_db
from app.core.security import security_manager
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the function from the main assessments file
import importlib.util
spec = importlib.util.spec_from_file_location("assessments", "app/api/assessments.py")
assessments_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(assessments_module)
get_student_upcoming_assessments = assessments_module.get_student_upcoming_assessments
from app.models.models import UserModel

async def test_student_upcoming_direct():
    try:
        await init_db()
        db = await get_db()
        
        # Get a student
        student = await db.users.find_one({"email": "student1@el.student.com", "role": "student"})
        if not student:
            print("Student not found")
            return
            
        print(f"Testing student: {student['email']} (ID: {student['_id']})")
        
        # Create UserModel
        user_model = UserModel(
            id=str(student["_id"]),
            email=student["email"],
            username=student.get("username", student["email"]),
            role=student["role"],
            password_hash=student.get("password_hash", "dummy_hash")
        )
        
        # Call the endpoint function directly
        result = await get_student_upcoming_assessments(user_model)
        
        print(f"Result: {result}")
        print(f"Number of assessments: {len(result)}")
        
        for i, assessment in enumerate(result):
            print(f"Assessment {i+1}: {assessment.title} (ID: {assessment.id})")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_student_upcoming_direct())
