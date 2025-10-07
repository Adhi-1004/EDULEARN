#!/usr/bin/env python3
"""
Debug other collections
"""
import asyncio
import sys
import os
from bson import ObjectId

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.db import init_db, get_db

async def debug_other_collections():
    """Debug other collections"""
    print("Debugging other collections...")
    
    try:
        # Initialize database
        await init_db()
        db = await get_db()
        
        # Check assessment_results collection
        assessment_results = await db.assessment_results.find({}).to_list(length=None)
        print(f"📊 Assessment results: {len(assessment_results)}")
        for result in assessment_results[:2]:
            student_id = result.get('student_id')
            print(f"   - Student ID type: {type(student_id)}")
            print(f"   - Student ID value: {student_id}")
            print()
        
        # Check assessment_submissions collection
        submissions = await db.assessment_submissions.find({}).to_list(length=None)
        print(f"📊 Assessment submissions: {len(submissions)}")
        for result in submissions[:2]:
            student_id = result.get('student_id')
            print(f"   - Student ID type: {type(student_id)}")
            print(f"   - Student ID value: {student_id}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Debug failed: {str(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    asyncio.run(debug_other_collections())
