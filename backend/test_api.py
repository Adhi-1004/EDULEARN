#!/usr/bin/env python3
"""
Test API endpoint directly
"""
import asyncio
import sys
import os
from bson import ObjectId

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.db import init_db, get_db
from app.api.results import get_user_results
from app.models.models import UserModel

async def test_api():
    """Test API endpoint directly"""
    print("Testing API endpoint directly...")
    
    try:
        # Initialize database
        await init_db()
        db = await get_db()
        
        # Create a mock user for testing
        user = UserModel(
            id=ObjectId('68e22565189c7fd11b85adc6'),
            username='testuser',
            email='sharu@el.student.com',
            password_hash='test',
            role='student'
        )
        
        # Test the get_user_results function directly
        result = await get_user_results('68e22565189c7fd11b85adc6', user)
        
        print(f"✅ API test successful!")
        print(f"📊 Success: {result.success}")
        print(f"📊 Total results: {result.total}")
        print(f"📊 Number of results: {len(result.results)}")
        
        for i, test_result in enumerate(result.results[:3]):  # Show first 3
            print(f"   {i+1}. {test_result.test_name} - {test_result.score}/{test_result.total_questions} ({test_result.percentage:.1f}%)")
        
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {str(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    asyncio.run(test_api())
