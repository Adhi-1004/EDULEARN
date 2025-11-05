#!/usr/bin/env python3
"""
Test the student upcoming endpoint directly
"""
import asyncio
import requests
from app.db import get_db, init_db
from app.core.security import security_manager

async def test_student_upcoming():
    try:
        await init_db()
        db = await get_db()
        
        # Get a student
        student = await db.users.find_one({"email": "student1@el.student.com", "role": "student"})
        if not student:
            print("Student not found")
            return
            
        print(f"Testing student: {student['email']} (ID: {student['_id']})")
        
        # Generate valid token
        token = security_manager.create_access_token(
            data={"sub": str(student["_id"]), "email": student["email"], "role": student["role"]}
        )
        print(f"Generated token: {token[:50]}...")
        
        # Test the endpoint
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            "http://localhost:5001/api/assessments/student/upcoming",
            headers=headers
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.json()}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_student_upcoming())
