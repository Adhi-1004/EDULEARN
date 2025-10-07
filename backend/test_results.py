#!/usr/bin/env python3
"""
Test results endpoint
"""
import asyncio
import sys
import os
from bson import ObjectId

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.db import init_db, get_db

async def test_results():
    """Test results data"""
    print("Testing results data...")
    
    try:
        # Initialize database
        await init_db()
        db = await get_db()
        
        # Check what's in the results collection
        results = await db.results.find({}).to_list(length=None)
        print(f"📊 Results collection: {len(results)} documents")
        for result in results[:3]:  # Show first 3
            print(f"   - {result}")
        
        # Check assessment_results collection
        assessment_results = await db.assessment_results.find({}).to_list(length=None)
        print(f"📊 Assessment results collection: {len(assessment_results)} documents")
        for result in assessment_results[:3]:  # Show first 3
            print(f"   - {result}")
        
        # Check assessment_submissions collection
        submissions = await db.assessment_submissions.find({}).to_list(length=None)
        print(f"📊 Assessment submissions collection: {len(submissions)} documents")
        for result in submissions[:3]:  # Show first 3
            print(f"   - {result}")
        
        # Check assessments collection
        assessments = await db.assessments.find({}).to_list(length=None)
        print(f"📊 Assessments collection: {len(assessments)} documents")
        for result in assessments[:3]:  # Show first 3
            print(f"   - {result}")
        
        # Check users collection
        users = await db.users.find({}).to_list(length=None)
        print(f"📊 Users collection: {len(users)} documents")
        for user in users[:3]:  # Show first 3
            print(f"   - {user.get('email', 'No email')} ({user.get('role', 'No role')})")
        
        return True
        
    except Exception as e:
        print(f"❌ Results test failed: {str(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    asyncio.run(test_results())
