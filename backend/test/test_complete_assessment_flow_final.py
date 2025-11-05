#!/usr/bin/env python3
"""
Comprehensive test to verify the complete assessment flow
"""
import asyncio
import requests
from app.db import get_db, init_db
from app.core.security import security_manager
from bson import ObjectId

async def test_complete_assessment_flow():
    try:
        print("=" * 60)
        print("COMPREHENSIVE ASSESSMENT FLOW TEST")
        print("=" * 60)
        
        await init_db()
        db = await get_db()

        # 1. Get teacher
        print("\n1. GETTING TEACHER...")
        teacher = await db.users.find_one({"email": "sharu@el.teacher.com", "role": "teacher"})
        if not teacher:
            print("ERROR: Teacher not found")
            return
        print(f"SUCCESS: Found teacher {teacher['email']}")

        # 2. Get batch
        print("\n2. GETTING BATCH...")
        batch = await db.batches.find_one({"teacher_id": str(teacher["_id"])})
        if not batch:
            batch = await db.batches.find_one({"teacher_id": ObjectId(teacher["_id"])})
        if not batch:
            print("ERROR: No batch found")
            return
        print(f"SUCCESS: Found batch {batch.get('name')} with {len(batch.get('student_ids', []))} students")

        # 3. Get students
        print("\n3. GETTING STUDENTS...")
        students = await db.users.find({"batch_id": batch["_id"], "role": "student"}).to_list(length=10)
        print(f"SUCCESS: Found {len(students)} students in batch")
        for student in students:
            print(f"  - {student['email']} (ID: {student['_id']})")

        # 4. Create assessment directly in database
        print("\n4. CREATING ASSESSMENT IN DATABASE...")
        assessment_data = {
            "_id": ObjectId(),
            "title": "Final Test Assessment - Python Basics",
            "topic": "Python Programming",
            "difficulty": "medium",
            "question_count": 3,
            "questions": [
                {
                    "id": "q1",
                    "question": "What is Python?",
                    "options": ["A programming language", "A snake", "A type of coffee", "A car"],
                    "answer": "A",
                    "explanation": "Python is a programming language",
                    "difficulty": "medium",
                    "topic": "Python Programming"
                }
            ],
            "batches": [str(batch["_id"])],
            "teacher_id": teacher["_id"],
            "type": "ai_generated",
            "created_at": ObjectId().generation_time,
            "is_active": True,
            "status": "active",
            "published_at": ObjectId().generation_time
        }
        
        result = await db.teacher_assessments.insert_one(assessment_data)
        assessment_id = str(result.inserted_id)
        print(f"SUCCESS: Created assessment {assessment_data['title']} with ID {assessment_id}")

        # 5. Create notifications
        print("\n5. CREATING NOTIFICATIONS...")
        notifications = []
        for student in students:
            notification = {
                "student_id": str(student["_id"]),
                "type": "assessment_assigned",
                "title": f"New Assessment: {assessment_data['title']}",
                "message": f"A new {assessment_data['difficulty']} assessment on {assessment_data['topic']} has been assigned to you.",
                "assessment_id": assessment_id,
                "created_at": ObjectId().generation_time,
                "is_read": False
            }
            notifications.append(notification)
        
        if notifications:
            await db.notifications.insert_many(notifications)
            print(f"SUCCESS: Created {len(notifications)} notifications")

        # 6. Test student access to upcoming assessments
        print("\n6. TESTING STUDENT ACCESS...")
        for student in students[:2]:  # Test first 2 students
            print(f"\nTesting student: {student['email']}")
            
            # Test the database query directly
            student_batches = await db.batches.find({
                "student_ids": str(student["_id"])
            }).to_list(length=None)
            
            if student_batches:
                batch_ids = [str(batch["_id"]) for batch in student_batches]
                teacher_assessments = await db.teacher_assessments.find({
                    "batches": {"$in": batch_ids},
                    "is_active": True,
                    "status": {"$in": ["active", "published"]}
                }).to_list(length=None)
                
                print(f"  Database query found {len(teacher_assessments)} assessments")
                
                # Check if our new assessment is in the results
                our_assessment_found = any(str(assessment["_id"]) == assessment_id for assessment in teacher_assessments)
                print(f"  Our new assessment found: {our_assessment_found}")
                
                if our_assessment_found:
                    print(f"  SUCCESS: Student can see the new assessment!")
                else:
                    print(f"  ERROR: Student cannot see the new assessment")
            else:
                print(f"  ERROR: No batches found for student")

        # 7. Test notifications
        print("\n7. TESTING NOTIFICATIONS...")
        for student in students[:2]:
            notifications_count = await db.notifications.count_documents({
                "student_id": str(student["_id"]),
                "assessment_id": assessment_id
            })
            print(f"  {student['email']}: {notifications_count} notifications for this assessment")

        print("\n" + "=" * 60)
        print("TEST COMPLETED")
        print("=" * 60)
        print(f"Assessment ID: {assessment_id}")
        print(f"Batch: {batch.get('name')}")
        print(f"Students: {len(students)}")
        print(f"Notifications: {len(notifications)}")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_complete_assessment_flow())
