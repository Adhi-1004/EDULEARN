#!/usr/bin/env python3
import asyncio
from app.db import get_db, init_db
from bson import ObjectId

async def check_assessment():
    try:
        await init_db()
        db = await get_db()
        
        assessment_id = "68fa1c47727038d959e2dcd9"
        teacher_id = "68f931d527df80442ee821e6"
        
        print(f"Checking assessment: {assessment_id}")
        print(f"Teacher ID: {teacher_id}")
        
        # Check the assessment
        assessment = await db.teacher_assessments.find_one({"_id": ObjectId(assessment_id)})
        if assessment:
            print(f"Assessment found: {assessment.get('title', 'Untitled')}")
            print(f"Assessment teacher_id: {assessment.get('teacher_id')}")
            print(f"Assessment teacher_id type: {type(assessment.get('teacher_id'))}")
            print(f"Expected teacher_id: {teacher_id}")
            print(f"Expected teacher_id type: {type(teacher_id)}")
            
            # Check if they match
            if str(assessment.get('teacher_id')) == str(teacher_id):
                print("✅ Teacher IDs match!")
            else:
                print("❌ Teacher IDs don't match!")
        else:
            print("❌ Assessment not found")
        
        # Check all teacher assessments
        assessments = await db.teacher_assessments.find({}).to_list(length=10)
        print(f"\nAll teacher assessments:")
        for ass in assessments:
            print(f"  - {ass.get('title', 'Untitled')} (ID: {ass['_id']}, Teacher: {ass.get('teacher_id')})")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_assessment())
