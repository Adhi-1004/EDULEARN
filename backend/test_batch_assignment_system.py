#!/usr/bin/env python3
"""
Test script to verify batch assignment system works perfectly
"""
import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.db import init_db, get_db
from bson import ObjectId

async def test_batch_assignment_system():
    """Test the complete batch assignment system"""
    print("🧪 Testing Batch Assignment System...")
    
    try:
        await init_db()
        db = await get_db()
        
        # Test 1: Check if batch student_ids are in sync
        print("\n📊 Test 1: Checking batch-student synchronization...")
        batches = await db.batches.find({}).to_list(length=None)
        
        for batch in batches:
            batch_id = str(batch["_id"])
            student_ids_in_batch = batch.get("student_ids", [])
            
            # Find students with this batch_id
            students_in_batch = await db.users.find({
                "batch_id": batch_id,
                "role": "student"
            }).to_list(length=None)
            
            student_ids_from_users = [str(s["_id"]) for s in students_in_batch]
            
            print(f"  Batch {batch.get('name', 'Unknown')}:")
            print(f"    student_ids array: {len(student_ids_in_batch)} students")
            print(f"    users with batch_id: {len(student_ids_from_users)} students")
            
            # Check if they match
            if set(student_ids_in_batch) == set(student_ids_from_users):
                print(f"    ✅ Synchronized")
            else:
                print(f"    ❌ NOT synchronized")
                print(f"    Missing from array: {set(student_ids_from_users) - set(student_ids_in_batch)}")
                print(f"    Extra in array: {set(student_ids_in_batch) - set(student_ids_from_users)}")
        
        # Test 2: Check notification system
        print("\n📊 Test 2: Checking notification system...")
        notifications = await db.notifications.find({
            "type": {"$in": ["assessment_assigned", "teacher_assessment_assigned"]}
        }).sort("created_at", -1).limit(10).to_list(length=None)
        
        print(f"  Found {len(notifications)} recent assessment notifications")
        for notif in notifications[:5]:
            print(f"    - {notif.get('title', 'No title')} ({notif.get('type', 'unknown')})")
        
        # Test 3: Check assessment-batch assignments
        print("\n📊 Test 3: Checking assessment-batch assignments...")
        assessments = await db.assessments.find({
            "assigned_batches": {"$exists": True, "$ne": []}
        }).to_list(length=None)
        
        print(f"  Found {len(assessments)} assessments with batch assignments")
        for assessment in assessments[:3]:
            assigned_batches = assessment.get("assigned_batches", [])
            print(f"    - {assessment.get('title', 'Untitled')}: {len(assigned_batches)} batches")
        
        # Test 4: Check teacher assessments
        print("\n📊 Test 4: Checking teacher assessments...")
        try:
            teacher_assessments = await db.teacher_assessments.find({
                "batches": {"$exists": True, "$ne": []}
            }).to_list(length=None)
            print(f"  Found {len(teacher_assessments)} teacher assessments with batch assignments")
        except Exception as e:
            print(f"  Teacher assessments collection not found or error: {e}")
        
        print("\n✅ Batch assignment system test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    asyncio.run(test_batch_assignment_system())
