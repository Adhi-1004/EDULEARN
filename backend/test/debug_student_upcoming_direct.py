#!/usr/bin/env python3
"""
Direct database test to debug the student upcoming assessments issue
"""
import asyncio
from app.db import get_db, init_db
from bson import ObjectId

async def debug_student_upcoming_direct():
    try:
        await init_db()
        db = await get_db()
        
        # Get a student
        student = await db.users.find_one({"email": "student1@el.student.com", "role": "student"})
        if not student:
            print("Student not found")
            return
            
        print(f"STUDENT: {student['email']} (ID: {student['_id']})")
        
        # Step 1: Find batches containing this student
        print("\n1. FINDING BATCHES CONTAINING STUDENT:")
        student_batches = await db.batches.find({
            "student_ids": str(student["_id"])
        }).to_list(length=None)
        
        print(f"Found {len(student_batches)} batches:")
        for batch in student_batches:
            print(f"  - {batch.get('name')} (ID: {batch['_id']})")
        
        if not student_batches:
            print("No batches found for student")
            return
        
        batch_ids = [str(batch["_id"]) for batch in student_batches]
        print(f"Batch IDs: {batch_ids}")
        
        # Step 2: Find teacher assessments assigned to these batches
        print("\n2. FINDING TEACHER ASSESSMENTS:")
        teacher_assessments = await db.teacher_assessments.find({
            "batches": {"$in": batch_ids},
            "is_active": True,
            "status": {"$in": ["active", "published"]}
        }).to_list(length=None)
        
        print(f"Found {len(teacher_assessments)} teacher assessments:")
        for assessment in teacher_assessments:
            print(f"  - {assessment.get('title')} (ID: {assessment['_id']})")
            print(f"    Status: {assessment.get('status')}")
            print(f"    Is Active: {assessment.get('is_active')}")
            print(f"    Batches: {assessment.get('batches')}")
        
        # Step 3: Check submissions
        print("\n3. CHECKING SUBMISSIONS:")
        
        # Check regular submissions
        regular_submissions = await db.assessment_submissions.find({
            "student_id": student["_id"]
        }).to_list(length=None)
        print(f"Regular submissions: {len(regular_submissions)}")
        for sub in regular_submissions:
            print(f"  - Assessment ID: {sub.get('assessment_id')}")
        
        # Check teacher submissions
        teacher_submissions = await db.teacher_assessment_results.find({
            "student_id": student["_id"]
        }).to_list(length=None)
        print(f"Teacher submissions: {len(teacher_submissions)}")
        for sub in teacher_submissions:
            print(f"  - Assessment ID: {sub.get('assessment_id')}")
        
        # Step 4: Filter assessments
        print("\n4. FILTERING ASSESSMENTS:")
        submitted_ids = []
        submitted_ids.extend([str(sub.get("assessment_id")) for sub in regular_submissions if sub.get("assessment_id")])
        submitted_ids.extend([str(sub.get("assessment_id")) for sub in teacher_submissions if sub.get("assessment_id")])
        
        print(f"Submitted assessment IDs: {submitted_ids}")
        
        upcoming_assessments = [
            assessment for assessment in teacher_assessments 
            if str(assessment["_id"]) not in submitted_ids
        ]
        
        print(f"Upcoming assessments after filtering: {len(upcoming_assessments)}")
        for assessment in upcoming_assessments:
            print(f"  - {assessment.get('title')} (ID: {assessment['_id']})")
        
        # Step 5: Check if there's an issue with the query
        print("\n5. TESTING DIFFERENT QUERY CONDITIONS:")
        
        # Test without is_active filter
        test_query1 = await db.teacher_assessments.find({
            "batches": {"$in": batch_ids}
        }).to_list(length=None)
        print(f"Query without is_active filter: {len(test_query1)} assessments")
        
        # Test without status filter
        test_query2 = await db.teacher_assessments.find({
            "batches": {"$in": batch_ids},
            "is_active": True
        }).to_list(length=None)
        print(f"Query without status filter: {len(test_query2)} assessments")
        
        # Test with different status values
        test_query3 = await db.teacher_assessments.find({
            "batches": {"$in": batch_ids},
            "status": "active"
        }).to_list(length=None)
        print(f"Query with status='active' only: {len(test_query3)} assessments")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_student_upcoming_direct())
