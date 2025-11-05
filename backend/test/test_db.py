#!/usr/bin/env python3
"""
Test database connection
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

async def test_mongodb_connection():
    """Test MongoDB connection"""
    mongo_uri = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/edulearn")
    db_name = os.getenv("DB_NAME", "edulearn")
    
    print(f"Testing MongoDB connection...")
    print(f"URI: {mongo_uri}")
    print(f"Database: {db_name}")
    
    try:
        client = AsyncIOMotorClient(mongo_uri)
        db = client[db_name]
        
        # Test connection
        await client.admin.command('ping')
        print("✅ MongoDB connection successful!")
        
        # Test database operations
        result = await db.test_collection.insert_one({"test": "data"})
        print(f"✅ Insert test successful: {result.inserted_id}")
        
        # Clean up
        await db.test_collection.delete_one({"_id": result.inserted_id})
        print("✅ Delete test successful")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(test_mongodb_connection())
