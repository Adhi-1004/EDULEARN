#!/usr/bin/env python3
import asyncio
from app.db import get_db, init_db
from bson import ObjectId

async def test_endpoints():
    try:
        await init_db()
        db = await get_db()
        
        # Check if teacher_assessments collection exists and has data
        count = await db.teacher_assessments.count_documents({})
        print(f'Teacher assessments count: {count}')
        
        # Check if batches collection exists and has data
        count = await db.batches.count_documents({})
        print(f'Batches count: {count}')
        
        # Check if notifications collection exists
        count = await db.notifications.count_documents({})
        print(f'Notifications count: {count}')
        
        # Check if users collection exists
        count = await db.users.count_documents({})
        print(f'Users count: {count}')
        
        print("Database collections are accessible")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_endpoints())
