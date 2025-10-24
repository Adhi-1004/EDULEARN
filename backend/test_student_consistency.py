#!/usr/bin/env python3
"""
Test script to verify student consistency between dashboard and results
"""
import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.db import init_db, get_db
from bson import ObjectId

async def test_student_consistency():
    """Test student consistency between dashboard and results"""
    print("🧪 Testing Student Consistency...")
    
    try:
        await init_db()
        db = await get_db()
        
        # Get all batches
        batches = await db.batches.find({}).to_list(length=None)
        print(f"📊 Found {len(batches)} batches")
        
        all_consistent = True
        
        for batch in batches:
            batch_id = str(batch["_id"])
            batch_name = batch.get("name", "Unknown")
            print(f"\n🔍 Testing batch: {batch_name} ({batch_id})")
            
            # Method 1: Dashboard method (users.batch_id)
            students_via_batch_id = await db.users.find({
                "$or": [
                    {"batch_id": ObjectId(batch_id), "role": "student"},
                    {"batch_id": batch_id, "role": "student"}
                ]
            }).to_list(length=None)
            
            # Method 2: Result page method (batches.student_ids)
            batch_doc = await db.batches.find_one({"_id": ObjectId(batch_id)})
            student_ids_in_batch = batch_doc.get("student_ids", [])
            
            students_via_student_ids = []
            for student_id in student_ids_in_batch:
                try:
                    if ObjectId.is_valid(student_id):
                        student = await db.users.find_one({"_id": ObjectId(student_id)})
                    else:
                        student = await db.users.find_one({"_id": student_id})
                    if student:
                        students_via_student_ids.append(student)
                except Exception:
                    pass
            
            print(f"   Dashboard method: {len(students_via_batch_id)} students")
            print(f"   Result page method: {len(students_via_student_ids)} students")
            
            if len(students_via_batch_id) == len(students_via_student_ids):
                print(f"   ✅ CONSISTENT")
            else:
                print(f"   ❌ INCONSISTENT")
                all_consistent = False
                
                # Show details
                batch_id_student_ids = {str(s["_id"]) for s in students_via_batch_id}
                student_ids_set = set(student_ids_in_batch)
                
                missing_from_array = batch_id_student_ids - student_ids_set
                extra_in_array = student_ids_set - batch_id_student_ids
                
                if missing_from_array:
                    print(f"   Missing from batches.student_ids: {missing_from_array}")
                if extra_in_array:
                    print(f"   Extra in batches.student_ids: {extra_in_array}")
        
        if all_consistent:
            print(f"\n🎉 All batches are consistent!")
        else:
            print(f"\n❌ Some batches are inconsistent. Run sync_batch_student_data.py to fix.")
        
        return all_consistent
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    asyncio.run(test_student_consistency())
