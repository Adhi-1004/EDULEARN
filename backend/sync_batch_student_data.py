#!/usr/bin/env python3
"""
Comprehensive script to sync batch student data
Ensures users.batch_id and batches.student_ids are always in sync
"""
import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.db import init_db, get_db
from bson import ObjectId

async def sync_batch_student_data():
    """Sync batch student data to ensure consistency"""
    print("🔄 Syncing Batch Student Data...")
    
    try:
        await init_db()
        db = await get_db()
        
        # Get all batches
        batches = await db.batches.find({}).to_list(length=None)
        print(f"📊 Found {len(batches)} batches")
        
        total_fixes = 0
        
        for batch in batches:
            batch_id = str(batch["_id"])
            batch_name = batch.get("name", "Unknown")
            print(f"\n🔍 Processing batch: {batch_name} ({batch_id})")
            
            # Method 1: Get students via users.batch_id (dashboard method)
            students_via_batch_id = await db.users.find({
                "$or": [
                    {"batch_id": ObjectId(batch_id), "role": "student"},
                    {"batch_id": batch_id, "role": "student"}
                ]
            }).to_list(length=None)
            
            # Method 2: Get students via batches.student_ids (result page method)
            student_ids_in_batch = batch.get("student_ids", [])
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
            
            # Check for mismatches
            if len(students_via_batch_id) != len(students_via_student_ids):
                print(f"   ❌ MISMATCH DETECTED!")
                
                # Fix: Update batches.student_ids to match users.batch_id
                correct_student_ids = [str(s["_id"]) for s in students_via_batch_id]
                
                await db.batches.update_one(
                    {"_id": ObjectId(batch_id)},
                    {"$set": {"student_ids": correct_student_ids}}
                )
                
                print(f"   ✅ Fixed: Updated batches.student_ids to {len(correct_student_ids)} students")
                total_fixes += 1
                
                # Also ensure all students have correct batch_id
                for student in students_via_batch_id:
                    student_batch_id = student.get("batch_id")
                    if not student_batch_id or str(student_batch_id) != batch_id:
                        await db.users.update_one(
                            {"_id": student["_id"]},
                            {"$set": {"batch_id": batch_id}}
                        )
                        print(f"   ✅ Fixed: Updated student {student.get('email', 'Unknown')} batch_id")
            else:
                print(f"   ✅ Data is consistent")
        
        print(f"\n🎉 Sync completed! Fixed {total_fixes} batches")
        
        # Final verification
        print("\n🔍 Final verification...")
        for batch in batches:
            batch_id = str(batch["_id"])
            batch_name = batch.get("name", "Unknown")
            
            # Count via both methods
            count_via_batch_id = await db.users.count_documents({
                "$or": [
                    {"batch_id": ObjectId(batch_id), "role": "student"},
                    {"batch_id": batch_id, "role": "student"}
                ]
            })
            
            batch_doc = await db.batches.find_one({"_id": ObjectId(batch_id)})
            count_via_student_ids = len(batch_doc.get("student_ids", []))
            
            if count_via_batch_id == count_via_student_ids:
                print(f"   ✅ {batch_name}: {count_via_batch_id} students (consistent)")
            else:
                print(f"   ❌ {batch_name}: Dashboard={count_via_batch_id}, Results={count_via_student_ids} (STILL MISMATCHED)")
        
        return True
        
    except Exception as e:
        print(f"❌ Sync failed: {str(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    asyncio.run(sync_batch_student_data())
