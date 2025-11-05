#!/usr/bin/env python3
"""
Script to debug the student batch lookup issue
"""
import asyncio
from app.db import get_db, init_db
from bson import ObjectId

async def debug_student_batch():
    try:
        await init_db()
        db = await get_db()
        
        # Get a student
        student = await db.users.find_one({"email": "student1@el.student.com", "role": "student"})
        if not student:
            print("Student not found")
            return
            
        print(f"STUDENT: {student['email']} (ID: {student['_id']})")
        print(f"Student batch_id: {student.get('batch_id')}")
        print(f"Student batch_name: {student.get('batch_name')}")
        
        # Check what batches contain this student
        print("\nBATCHES CONTAINING THIS STUDENT:")
        batches_with_student = await db.batches.find({
            "student_ids": str(student["_id"])
        }).to_list(length=None)
        
        print(f"Found {len(batches_with_student)} batches containing student:")
        for batch in batches_with_student:
            print(f"  - {batch.get('name')} (ID: {batch['_id']})")
            print(f"    Student IDs: {batch.get('student_ids')}")
        
        if batches_with_student:
            batch_ids = [str(batch["_id"]) for batch in batches_with_student]
            print(f"\nBatch IDs to search: {batch_ids}")
            
            # Test the exact query from the student upcoming endpoint
            print("\nTESTING STUDENT UPCOMING QUERY:")
            teacher_assessments = await db.teacher_assessments.find({
                "batches": {"$in": batch_ids},
                "is_active": True,
                "status": {"$in": ["active", "published"]}
            }).to_list(length=None)
            
            print(f"Found {len(teacher_assessments)} teacher assessments:")
            for assessment in teacher_assessments:
                print(f"  - {assessment.get('title')} (ID: {assessment['_id']})")
                print(f"    Batches: {assessment.get('batches')}")
                print(f"    Status: {assessment.get('status')}")
                print(f"    Is Active: {assessment.get('is_active')}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_student_batch())
