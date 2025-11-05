#!/usr/bin/env python3
import asyncio
import json
import requests
from app.db import get_db, init_db
from app.core.security import security_manager
from bson import ObjectId

async def test_complete_flow():
    try:
        await init_db()
        db = await get_db()
        
        # Get a teacher user
        teacher = await db.users.find_one({"role": "teacher"})
        if not teacher:
            print("No teacher found in database")
            return
        
        print(f"Found teacher: {teacher.get('email', 'Unknown')}")
        
        # Generate a token for the teacher
        token = security_manager.create_access_token(
            data={"sub": str(teacher["_id"]), "email": teacher["email"], "role": teacher["role"]}
        )
        
        print(f"Generated token: {token}")
        
        # Check existing batches
        batches = await db.batches.find({}).to_list(length=10)
        print(f"Found {len(batches)} batches:")
        for batch in batches:
            print(f"  - {batch.get('name', 'Unknown')} (ID: {batch['_id']}, Teacher: {batch.get('teacher_id')})")
        
        # Use existing batch for the teacher
        batch = await db.batches.find_one({"teacher_id": str(teacher["_id"])})
        if not batch:
            # Try with ObjectId comparison as well
            batch = await db.batches.find_one({"teacher_id": ObjectId(teacher["_id"])})
        if not batch:
            print("No batch found for teacher")
            return
        
        print(f"Using batch: {batch.get('name', 'Unknown')} (ID: {batch['_id']})")
        
        # Add a student to the batch
        student = await db.users.find_one({"role": "student"})
        if student:
            print(f"Adding student {student.get('email', 'Unknown')} to batch...")
            
            # Update student's batch
            await db.users.update_one(
                {"_id": student["_id"]},
                {
                    "$set": {
                        "batch_id": batch["_id"],
                        "batch_name": batch["name"]
                    }
                }
            )
            
            # Add student to batch's student list
            await db.batches.update_one(
                {"_id": batch["_id"]},
                {"$addToSet": {"student_ids": str(student["_id"])}}
            )
            
            print(f"SUCCESS: Student added to batch!")
        
        # Test creating an assessment
        assessment_data = {
            "title": "Test Assessment - Python Basics",
            "topic": "Python Programming",
            "difficulty": "medium",
            "question_count": 5,
            "batches": [str(batch["_id"])],
            "type": "ai_generated"
        }
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        print("Creating assessment...")
        response = requests.post(
            "http://localhost:5001/api/teacher/assessments/create",
            headers=headers,
            json=assessment_data
        )
        
        if response.status_code == 200:
            result = response.json()
            assessment_id = result.get("assessment_id")
            print(f"SUCCESS: Assessment created successfully! ID: {assessment_id}")
            
            # Test assigning batches
            print("Assigning batches...")
            assign_response = requests.post(
                f"http://localhost:5001/api/assessments/teacher/{assessment_id}/assign-batches",
                headers=headers,
                json=[str(batch["_id"])]
            )
            
            if assign_response.status_code == 200:
                print("SUCCESS: Batches assigned successfully!")
                
                # Test publishing
                print("Publishing assessment...")
                publish_response = requests.post(
                    f"http://localhost:5001/api/assessments/teacher/{assessment_id}/publish",
                    headers=headers
                )
                
                if publish_response.status_code == 200:
                    print("SUCCESS: Assessment published successfully!")
                    
                    # Check if students can see the assessment
                    print("Checking student access...")
                    students = await db.users.find({"batch_id": batch["_id"], "role": "student"}).to_list(length=5)
                    print(f"Found {len(students)} students in batch")
                    
                    for student in students:
                        print(f"  - {student.get('email', 'Unknown')} (ID: {student['_id']})")
                    
                    print("\nSUCCESS: Complete assessment flow test successful!")
                    print(f"Assessment ID: {assessment_id}")
                    print(f"Batch: {batch['name']}")
                    print(f"Students: {len(students)}")
                    
                else:
                    print(f"ERROR: Failed to publish assessment: {publish_response.text}")
            else:
                print(f"ERROR: Failed to assign batches: {assign_response.text}")
        else:
            print(f"ERROR: Failed to create assessment: {response.text}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_complete_flow())