#!/usr/bin/env python3
"""
Test script to debug the complete assessment creation and student visibility flow
with comprehensive logging
"""
import asyncio
import json
import requests
from app.db import get_db, init_db
from app.core.security import security_manager
from bson import ObjectId

async def test_debug_flow():
    try:
        print("[DEBUG-FLOW] Starting comprehensive debug test...")
        await init_db()
        db = await get_db()

        print("\n1. [DEBUG-FLOW] Getting teacher credentials...")
        teacher = await db.users.find_one({"email": "sharu@el.teacher.com", "role": "teacher"})
        if not teacher:
            print("ERROR [DEBUG-FLOW] Teacher not found")
            return
        print(f"SUCCESS [DEBUG-FLOW] Found teacher: {teacher['email']} (ID: {teacher['_id']})")

        token = security_manager.create_access_token(
            data={"sub": str(teacher["_id"]), "email": teacher["email"], "role": teacher["role"]}
        )
        print(f"TOKEN [DEBUG-FLOW] Generated token: {token[:50]}...")
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Get batch information
        print("\n2. [DEBUG-FLOW] Getting batch information...")
        batch = await db.batches.find_one({"teacher_id": str(teacher["_id"])})
        if not batch:
            batch = await db.batches.find_one({"teacher_id": ObjectId(teacher["_id"])})
        if not batch:
            print("ERROR [DEBUG-FLOW] No batch found for teacher")
            return
        
        print(f"SUCCESS [DEBUG-FLOW] Found batch: {batch.get('name', 'Unknown')} (ID: {batch['_id']})")
        print(f"STUDENTS [DEBUG-FLOW] Batch student IDs: {batch.get('student_ids', [])}")
        
        # 3. Check students in batch
        print("\n3. [DEBUG-FLOW] Checking students in batch...")
        students_in_batch = await db.users.find({"batch_id": batch["_id"], "role": "student"}).to_list(length=10)
        print(f"COUNT [DEBUG-FLOW] Found {len(students_in_batch)} students in batch:")
        for student in students_in_batch:
            print(f"  - {student.get('email', 'Unknown')} (ID: {student['_id']})")

        # 4. Create assessment
        print("\n4. [DEBUG-FLOW] Creating assessment...")
        assessment_data = {
            "title": "Debug Test Assessment - Python Basics",
            "topic": "Python Programming",
            "difficulty": "medium",
            "question_count": 3,
            "batches": [str(batch["_id"])],
            "type": "ai_generated"
        }
        print(f"SEND [DEBUG-FLOW] Assessment data: {assessment_data}")
        
        response = requests.post(
            "http://localhost:5001/api/teacher/assessments/create",
            headers=headers,
            json=assessment_data
        )

        if response.status_code == 200:
            result = response.json()
            assessment_id = result.get("assessment_id")
            print(f"SUCCESS [DEBUG-FLOW] Assessment created successfully! ID: {assessment_id}")
        else:
            print(f"ERROR [DEBUG-FLOW] Failed to create assessment: {response.text}")
            return

        # 5. Assign batches
        print("\n5. [DEBUG-FLOW] Assigning batches...")
        assign_response = requests.post(
            f"http://localhost:5001/api/assessments/teacher/{assessment_id}/assign-batches",
            headers=headers,
            json=[str(batch["_id"])]
        )

        if assign_response.status_code == 200:
            print(f"SUCCESS [DEBUG-FLOW] Batches assigned successfully!")
            print(f"RESPONSE [DEBUG-FLOW] Response: {assign_response.json()}")
        else:
            print(f"ERROR [DEBUG-FLOW] Failed to assign batches: {assign_response.text}")
            return

        # 6. Publish assessment
        print("\n6. [DEBUG-FLOW] Publishing assessment...")
        publish_response = requests.post(
            f"http://localhost:5001/api/assessments/teacher/{assessment_id}/publish",
            headers=headers
        )

        if publish_response.status_code == 200:
            print(f"SUCCESS [DEBUG-FLOW] Assessment published successfully!")
            print(f"RESPONSE [DEBUG-FLOW] Response: {publish_response.json()}")
        else:
            print(f"ERROR [DEBUG-FLOW] Failed to publish assessment: {publish_response.text}")
            return

        # 7. Check notifications created
        print("\n7. [DEBUG-FLOW] Checking notifications...")
        notifications = await db.notifications.find({"assessment_id": assessment_id}).to_list(length=10)
        print(f"COUNT [DEBUG-FLOW] Found {len(notifications)} notifications for assessment:")
        for notification in notifications:
            print(f"  - Student: {notification.get('student_id')} - {notification.get('title')}")

        # 8. Test student access to upcoming assessments
        print("\n8. [DEBUG-FLOW] Testing student access to upcoming assessments...")
        for student in students_in_batch[:2]:  # Test first 2 students
            print(f"\nSTUDENT [DEBUG-FLOW] Testing student: {student['email']} (ID: {student['_id']})")
            
            # Generate student token
            student_token = security_manager.create_access_token(
                data={"sub": str(student["_id"]), "email": student["email"], "role": student["role"]}
            )
            student_headers = {"Authorization": f"Bearer {student_token}"}
            
            # Test upcoming assessments endpoint
            upcoming_response = requests.get(
                "http://localhost:5001/api/assessments/student/upcoming",
                headers=student_headers
            )
            
            if upcoming_response.status_code == 200:
                upcoming_data = upcoming_response.json()
                print(f"SUCCESS [DEBUG-FLOW] Student can access upcoming assessments")
                print(f"COUNT [DEBUG-FLOW] Found {len(upcoming_data)} upcoming assessments")
                for assessment in upcoming_data:
                    print(f"  - {assessment.get('title', 'Untitled')} (ID: {assessment.get('id')})")
            else:
                print(f"ERROR [DEBUG-FLOW] Student cannot access upcoming assessments: {upcoming_response.text}")

            # Test notifications endpoint
            notifications_response = requests.get(
                "http://localhost:5001/api/notifications/",
                headers=student_headers
            )
            
            if notifications_response.status_code == 200:
                notifications_data = notifications_response.json()
                print(f"SUCCESS [DEBUG-FLOW] Student can access notifications")
                print(f"COUNT [DEBUG-FLOW] Found {len(notifications_data.get('notifications', []))} notifications")
                for notification in notifications_data.get('notifications', []):
                    print(f"  - {notification.get('title', 'No title')} - {notification.get('type', 'No type')}")
            else:
                print(f"ERROR [DEBUG-FLOW] Student cannot access notifications: {notifications_response.text}")

        print("\nCOMPLETE [DEBUG-FLOW] Debug test completed!")
        print(f"SUMMARY [DEBUG-FLOW] Summary:")
        print(f"  - Assessment ID: {assessment_id}")
        print(f"  - Batch: {batch['name']}")
        print(f"  - Students in batch: {len(students_in_batch)}")
        print(f"  - Notifications created: {len(notifications)}")

    except Exception as e:
        print(f"ERROR [DEBUG-FLOW] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_debug_flow())
