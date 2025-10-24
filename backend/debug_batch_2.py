#!/usr/bin/env python3
"""
Debug script to check batch 2 student data
"""
import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.db import init_db, get_db
from bson import ObjectId

async def debug_batch_2():
    """Debug batch 2 student data"""
    print("🔍 Debugging Batch 2 Student Data...")
    
    try:
        await init_db()
        db = await get_db()
        
        # Find batch 2
        batch_2 = await db.batches.find_one({"name": "Batch 2"})
        if not batch_2:
            print("❌ Batch 2 not found")
            return
        
        batch_id = str(batch_2["_id"])
        print(f"📊 Batch 2 ID: {batch_id}")
        print(f"📊 Batch 2 Name: {batch_2.get('name', 'Unknown')}")
        
        # Method 1: Count via users.batch_id (dashboard method)
        students_via_batch_id = await db.users.find({
            "batch_id": batch_id,
            "role": "student"
        }).to_list(length=None)
        
        print(f"\n📊 Method 1 (Dashboard): Students via users.batch_id")
        print(f"   Count: {len(students_via_batch_id)}")
        for student in students_via_batch_id:
            print(f"   - {student.get('name', 'Unknown')} ({student.get('email', 'No email')}) - ID: {student['_id']}")
        
        # Method 2: Count via batches.student_ids (result page method)
        student_ids_in_batch = batch_2.get("student_ids", [])
        print(f"\n📊 Method 2 (Result Page): Students via batches.student_ids")
        print(f"   Array length: {len(student_ids_in_batch)}")
        print(f"   Student IDs: {student_ids_in_batch}")
        
        students_via_student_ids = []
        for student_id in student_ids_in_batch:
            try:
                if ObjectId.is_valid(student_id):
                    student = await db.users.find_one({"_id": ObjectId(student_id)})
                else:
                    student = await db.users.find_one({"_id": student_id})
                
                if student:
                    students_via_student_ids.append(student)
                    print(f"   - {student.get('name', 'Unknown')} ({student.get('email', 'No email')}) - ID: {student['_id']}")
                else:
                    print(f"   - ❌ Student not found: {student_id}")
            except Exception as e:
                print(f"   - ❌ Error finding student {student_id}: {e}")
        
        # Check for mismatches
        print(f"\n🔍 Analysis:")
        print(f"   Dashboard count: {len(students_via_batch_id)}")
        print(f"   Result page count: {len(students_via_student_ids)}")
        
        if len(students_via_batch_id) != len(students_via_student_ids):
            print(f"   ❌ MISMATCH DETECTED!")
            
            # Find students in batch_id but not in student_ids
            batch_id_student_ids = {str(s["_id"]) for s in students_via_batch_id}
            student_ids_set = set(student_ids_in_batch)
            
            missing_from_array = batch_id_student_ids - student_ids_set
            extra_in_array = student_ids_set - batch_id_student_ids
            
            if missing_from_array:
                print(f"   Students in batch_id but missing from student_ids array: {missing_from_array}")
            if extra_in_array:
                print(f"   Student IDs in array but not in batch_id: {extra_in_array}")
        else:
            print(f"   ✅ Counts match!")
        
        return True
        
    except Exception as e:
        print(f"❌ Debug failed: {str(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    asyncio.run(debug_batch_2())
