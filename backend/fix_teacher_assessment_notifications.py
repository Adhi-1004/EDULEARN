#!/usr/bin/env python3
"""
Fix teacher assessment notifications for existing assessments
"""
import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.db import init_db, get_db
from bson import ObjectId
from datetime import datetime

async def fix_teacher_assessment_notifications():
    """Fix teacher assessment notifications"""
    print("🔧 Fixing Teacher Assessment Notifications...")
    
    try:
        await init_db()
        db = await get_db()
        
        # Find all published teacher assessments
        teacher_assessments = await db.teacher_assessments.find({
            "status": "published",
            "is_active": True
        }).to_list(length=None)
        
        print(f"📊 Found {len(teacher_assessments)} published teacher assessments")
        
        total_notifications_sent = 0
        
        for assessment in teacher_assessments:
            assessment_id = str(assessment["_id"])
            title = assessment.get("title", "Untitled")
            batches = assessment.get("batches", [])
            
            print(f"\n🔍 Processing assessment: {title} (ID: {assessment_id})")
            print(f"   Batches: {batches}")
            
            # Check if notifications already exist
            existing_notifications = await db.notifications.find({
                "assessment_id": assessment_id,
                "type": "teacher_assessment_assigned"
            }).to_list(length=None)
            
            print(f"   Existing notifications: {len(existing_notifications)}")
            
            if len(existing_notifications) == 0:
                print(f"   ❌ No notifications found, creating them...")
                
                # Get all students from batches using dashboard method
                student_ids = []
                for batch_id in batches:
                    students_in_batch = await db.users.find({
                        "$or": [
                            {"batch_id": ObjectId(batch_id), "role": "student"},
                            {"batch_id": batch_id, "role": "student"}
                        ]
                    }).to_list(length=None)
                    
                    for student in students_in_batch:
                        student_ids.append(str(student["_id"]))
                    
                    print(f"   Found {len(students_in_batch)} students in batch {batch_id}")
                
                # Create notifications
                notifications = []
                for student_id in student_ids:
                    notification = {
                        "student_id": student_id,
                        "type": "teacher_assessment_assigned",
                        "title": f"New Assessment: {title}",
                        "message": f"A new {assessment.get('difficulty', 'medium')} assessment on {assessment.get('topic', 'General')} has been assigned to you.",
                        "assessment_id": assessment_id,
                        "created_at": datetime.utcnow(),
                        "is_read": False
                    }
                    notifications.append(notification)
                
                if notifications:
                    await db.notifications.insert_many(notifications)
                    print(f"   ✅ Created {len(notifications)} notifications")
                    total_notifications_sent += len(notifications)
                else:
                    print(f"   ⚠️ No students found in batches")
            else:
                print(f"   ✅ Notifications already exist")
        
        print(f"\n🎉 Fix completed! Sent {total_notifications_sent} notifications")
        
        return True
        
    except Exception as e:
        print(f"❌ Fix failed: {str(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    asyncio.run(fix_teacher_assessment_notifications())
