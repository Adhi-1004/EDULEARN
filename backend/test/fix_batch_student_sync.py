"""
Utility Script: Fix Batch-Student Synchronization
Ensures batch.student_ids and user.batch_ids are in sync
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db import get_db, init_db
from bson import ObjectId


async def fix_batch_student_sync():
    """Synchronize batch student_ids with user batch_ids"""
    
    print("[FIX] Starting batch-student synchronization...")
    print("[FIX] Initializing database connection...")
    
    await init_db()
    db = await get_db()
    
    # Step 1: Get all batches
    print("\n[STEP 1] Fetching all batches...")
    batches = await db.batches.find({}).to_list(length=None)
    print(f"[INFO] Found {len(batches)} batches")
    
    fixed_count = 0
    
    for batch in batches:
        batch_id = str(batch["_id"])
        batch_name = batch.get("name", "Unknown")
        student_ids_in_batch = batch.get("student_ids", [])
        
        print(f"\n[BATCH] Processing: {batch_name} (ID: {batch_id})")
        print(f"  - Students in batch.student_ids: {len(student_ids_in_batch)}")
        print(f"  - Student IDs: {student_ids_in_batch}")
        
        # Step 2: For each student in batch, ensure they have batch_id in their batch_ids array
        for student_id in student_ids_in_batch:
            try:
                # Try to find student
                student = None
                if ObjectId.is_valid(student_id):
                    student = await db.users.find_one({"_id": ObjectId(student_id)})
                if not student:
                    student = await db.users.find_one({"_id": student_id})
                
                if not student:
                    print(f"  [WARN] Student {student_id} not found, removing from batch")
                    await db.batches.update_one(
                        {"_id": batch["_id"]},
                        {"$pull": {"student_ids": student_id}}
                    )
                    continue
                
                student_batch_ids = student.get("batch_ids", [])
                print(f"  - Student {student.get('email', student_id)} has batch_ids: {student_batch_ids}")
                
                # Ensure student has batch_ids array
                if not isinstance(student_batch_ids, list):
                    print(f"  [FIX] Converting batch_ids to array for student {student.get('email', student_id)}")
                    student_batch_ids = []
                
                if not student_batch_ids:
                    print(f"  [FIX] Adding batch_ids array to student {student.get('email', student_id)}")
                    await db.users.update_one(
                        {"_id": student["_id"]},
                        {"$set": {"batch_ids": [batch_id]}}
                    )
                    fixed_count += 1
                elif batch_id not in student_batch_ids:
                    print(f"  [FIX] Adding batch {batch_id} to student {student.get('email', student_id)}")
                    await db.users.update_one(
                        {"_id": student["_id"]},
                        {"$addToSet": {"batch_ids": batch_id}}
                    )
                    fixed_count += 1
                else:
                    print(f"  [OK] Student {student.get('email', student_id)} already has batch")
                    
            except Exception as e:
                print(f"  [ERROR] Failed to process student {student_id}: {str(e)}")
    
    # Step 3: Find students with batch_ids not in any batch's student_ids and add them
    print("\n[STEP 2] Checking for students missing from batch.student_ids...")
    students_with_batches = await db.users.find({
        "batch_ids": {"$exists": True, "$ne": []},
        "role": "student"
    }).to_list(length=None)
    
    print(f"[INFO] Found {len(students_with_batches)} students with batch_ids")
    
    for student in students_with_batches:
        student_id = str(student["_id"])
        student_email = student.get("email", student_id)
        student_batch_ids = student.get("batch_ids", [])
        
        for batch_id in student_batch_ids:
            try:
                batch = None
                if ObjectId.is_valid(batch_id):
                    batch = await db.batches.find_one({"_id": ObjectId(batch_id)})
                if not batch:
                    batch = await db.batches.find_one({"_id": batch_id})
                
                if not batch:
                    print(f"  [WARN] Batch {batch_id} not found for student {student_email}, removing")
                    await db.users.update_one(
                        {"_id": student["_id"]},
                        {"$pull": {"batch_ids": batch_id}}
                    )
                    continue
                
                batch_student_ids = batch.get("student_ids", [])
                if student_id not in batch_student_ids:
                    print(f"  [FIX] Adding student {student_email} to batch {batch.get('name', batch_id)}")
                    await db.batches.update_one(
                        {"_id": batch["_id"]},
                        {"$addToSet": {"student_ids": student_id}}
                    )
                    fixed_count += 1
                    
            except Exception as e:
                print(f"  [ERROR] Failed to process batch {batch_id}: {str(e)}")
    
    print("\n" + "=" * 60)
    print("[SUMMARY] Synchronization Summary:")
    print(f"  Total fixes applied: {fixed_count}")
    print("=" * 60)
    
    return fixed_count


if __name__ == "__main__":
    print("=" * 60)
    print(" Batch-Student Synchronization Fix")
    print("=" * 60)
    print()
    
    result = asyncio.run(fix_batch_student_sync())
    
    print()
    if result > 0:
        print(f"[SUCCESS] Fixed {result} sync issues!")
    else:
        print("[SUCCESS] No issues found - everything is in sync!")
    
    sys.exit(0)

