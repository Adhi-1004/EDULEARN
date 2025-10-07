#!/usr/bin/env python3
"""
Debug user ID format
"""
import asyncio
import sys
import os
from bson import ObjectId

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.db import init_db, get_db

async def debug_user_id():
    """Debug user ID format"""
    print("Debugging user ID format...")
    
    try:
        # Initialize database
        await init_db()
        db = await get_db()
        
        # Check the exact user ID in the results
        results = await db.results.find({}).to_list(length=None)
        print(f"📊 Found {len(results)} results")
        
        for result in results[:3]:
            user_id = result.get('user_id')
            print(f"   - User ID type: {type(user_id)}")
            print(f"   - User ID value: {user_id}")
            print(f"   - User ID str: {str(user_id)}")
            print(f"   - Is ObjectId: {isinstance(user_id, ObjectId)}")
            print()
        
        # Test query with different formats
        test_user_id = '68e22565189c7fd11b85adc6'
        print(f"🔍 Testing query with string: {test_user_id}")
        
        # Query with string
        string_results = await db.results.find({"user_id": test_user_id}).to_list(length=None)
        print(f"   - String query results: {len(string_results)}")
        
        # Query with ObjectId
        object_id_results = await db.results.find({"user_id": ObjectId(test_user_id)}).to_list(length=None)
        print(f"   - ObjectId query results: {len(object_id_results)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Debug failed: {str(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    asyncio.run(debug_user_id())
