#!/usr/bin/env python3
"""
Test script to verify teacher assessment flow
"""
import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.db import init_db, get_db
from bson import ObjectId

async def test_teacher_assessment_flow():
    """Test teacher assessment flow"""
    print("🧪 Testing Teacher Assessment Flow...")
    
    try:
        await init_db()
        db = await get_db()
        
        # Find a teacher assessment
        teacher_assessments = await db.teacher_assessments.find({
            "status": "published",
            "is_active": True
        }).to_list(length=None)
        
        print(f"📊 Found {len(teacher_assessments)} published teacher assessments")
        
        for assessment in teacher_assessments:
            assessment_id = str(assessment["_id"])
            title = assessment.get("title", "Untitled")
            batches = assessment.get("batches", [])
            
            print(f"\n🔍 Assessment: {title} (ID: {assessment_id})")
            print(f"   Batches: {batches}")
            
            # Check how many students should receive this assessment
            total_students = 0
            for batch_id in batches:
                # Method 1: Via users.batch_id (dashboard method)
                students_via_batch_id = await db.users.find({
                    "$or": [
                        {"batch_id": ObjectId(batch_id), "role": "student"},
                        {"batch_id": batch_id, "role": "student"}
                    ]
                }).to_list(length=None)
                
                # Method 2: Via batches.student_ids (result page method)
                batch_doc = await db.batches.find_one({"_id": ObjectId(batch_id)})
                student_ids_in_batch = batch_doc.get("student_ids", []) if batch_doc else []
                
                print(f"   Batch {batch_id}:")
                print(f"     Dashboard method: {len(students_via_batch_id)} students")
                print(f"     Result page method: {len(student_ids_in_batch)} students")
                
                total_students += len(students_via_batch_id)
            
            # Check notifications sent for this assessment
            notifications = await db.notifications.find({
                "assessment_id": assessment_id,
                "type": "teacher_assessment_assigned"
            }).to_list(length=None)
            
            print(f"   Notifications sent: {len(notifications)}")
            
            # Check if students can see this assessment in upcoming
            if batches:
                # Test with first batch
                test_batch_id = batches[0]
                students_in_batch = await db.users.find({
                    "$or": [
                        {"batch_id": ObjectId(test_batch_id), "role": "student"},
                        {"batch_id": test_batch_id, "role": "student"}
                    ]
                }).limit(1).to_list(length=None)
                
                if students_in_batch:
                    test_student = students_in_batch[0]
                    student_id = str(test_student["_id"])
                    
                    # Check if this student would see the assessment
                    student_batch_id = test_student.get("batch_id")
                    if student_batch_id:
                        if isinstance(student_batch_id, ObjectId):
                            student_batch_id = str(student_batch_id)
                        
                        # Check if assessment is in student's batches
                        if student_batch_id in batches:
                            print(f"   ✅ Student {student_id} should see this assessment")
                        else:
                            print(f"   ❌ Student {student_id} won't see this assessment (batch mismatch)")
                    else:
                        print(f"   ❌ Student {student_id} has no batch_id")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    asyncio.run(test_teacher_assessment_flow())
