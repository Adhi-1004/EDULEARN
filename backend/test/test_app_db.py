#!/usr/bin/env python3
"""
Test application database connection
"""
import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.db import init_db, get_db

async def test_app_db():
    """Test application database connection"""
    print("Testing application database connection...")
    
    try:
        # Initialize database
        await init_db()
        print("✅ Database initialization successful")
        
        # Get database instance
        db = await get_db()
        print(f"✅ Database instance: {type(db)}")
        
        # Test inserting data
        result = await db.test_collection.insert_one({"test": "app_db_test"})
        print(f"✅ Insert test successful: {result.inserted_id}")
        
        # Test querying data
        doc = await db.test_collection.find_one({"_id": result.inserted_id})
        print(f"✅ Query test successful: {doc}")
        
        # Clean up
        await db.test_collection.delete_one({"_id": result.inserted_id})
        print("✅ Delete test successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Application database test failed: {str(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    asyncio.run(test_app_db())
