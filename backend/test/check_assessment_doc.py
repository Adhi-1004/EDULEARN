#!/usr/bin/env python3
"""
Quick script to check the actual assessment document in the database
"""
import asyncio
from app.db import get_db, init_db
from bson import ObjectId

async def check_assessment():
    try:
        await init_db()
        db = await get_db()
        
        # Get the latest assessment
        assessment = await db.teacher_assessments.find_one({}, sort=[("_id", -1)])
        if assessment:
            print("LATEST ASSESSMENT DOCUMENT:")
            print(f"ID: {assessment['_id']}")
            print(f"Title: {assessment.get('title')}")
            print(f"Status: {assessment.get('status')}")
            print(f"Is Active: {assessment.get('is_active')}")
            print(f"Batches: {assessment.get('batches')}")
            print(f"Teacher ID: {assessment.get('teacher_id')}")
            print(f"Published At: {assessment.get('published_at')}")
            print(f"Questions Count: {len(assessment.get('questions', []))}")
            
            # Check if it matches our query conditions
            print("\nQUERY CONDITIONS CHECK:")
            print(f"Batches match: {assessment.get('batches')}")
            print(f"Is Active True: {assessment.get('is_active') == True}")
            print(f"Status in ['active', 'published']: {assessment.get('status') in ['active', 'published']}")
            
            # Test the exact query
            print("\nTESTING EXACT QUERY:")
            batch_ids = assessment.get('batches', [])
            if batch_ids:
                query_result = await db.teacher_assessments.find({
                    "batches": {"$in": batch_ids},
                    "is_active": True,
                    "status": {"$in": ["active", "published"]}
                }).to_list(length=None)
                print(f"Query returned {len(query_result)} assessments")
                for result in query_result:
                    print(f"  - {result.get('title')} (Status: {result.get('status')}, Active: {result.get('is_active')})")
        else:
            print("No assessments found")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_assessment())
