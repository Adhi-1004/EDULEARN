#!/usr/bin/env python3
"""
Check the actual fields in assessment documents
"""
import asyncio
from app.db import get_db, init_db
from bson import ObjectId

async def check_assessment_fields():
    try:
        await init_db()
        db = await get_db()
        
        # Get a teacher assessment
        assessment = await db.teacher_assessments.find_one({}, sort=[("_id", -1)])
        if assessment:
            print("ASSESSMENT FIELDS:")
            for key, value in assessment.items():
                print(f"  {key}: {value} (type: {type(value)})")
        else:
            print("No assessments found")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_assessment_fields())
