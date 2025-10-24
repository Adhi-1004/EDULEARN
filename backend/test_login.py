#!/usr/bin/env python3
"""
Test login functionality with both email and roll number
"""
import asyncio
import sys
import os
from bson import ObjectId

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.db import init_db, get_db
from app.api.auth import login_user
from app.schemas.schemas import UserLogin
from app.models.models import UserModel
from app.utils.auth_utils import get_password_hash

async def test_login():
    """Test login functionality with both email and roll number"""
    print("Testing login functionality...")
    
    try:
        # Initialize database
        await init_db()
        db = await get_db()
        
        # Create a test student with roll number
        test_roll_number = "TEST001"
        test_email = "test.student@example.com"
        test_password = test_roll_number  # Password is same as roll number
        
        # Hash the password
        password_hash = get_password_hash(test_password)
        
        # Create student document
        student_doc = {
            "username": test_email,
            "email": test_email,
            "password_hash": password_hash,
            "role": "student",
            "batch_id": str(ObjectId()),
            "roll_number": test_roll_number,
            "full_name": "Test Student",
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z",
            "last_login": None,
            "profile_completed": False,
            "created_by": "test",
            "login_method": "roll_number"
        }
        
        # Insert test student
        result = await db.users.insert_one(student_doc)
        student_id = result.inserted_id
        print(f"✅ Created test student with ID: {student_id}")
        
        # Test 1: Login with email
        print("\n🧪 Test 1: Login with email")
        try:
            login_data = UserLogin(email=test_email, password=test_password)
            response = await login_user(login_data)
            
            if response["success"]:
                print(f"✅ Email login successful!")
                print(f"   User: {response['user']['name']} ({response['user']['email']})")
                print(f"   Role: {response['user']['role']}")
                print(f"   Roll Number: {response['user'].get('roll_number', 'N/A')}")
            else:
                print(f"❌ Email login failed: {response.get('message', 'Unknown error')}")
        except Exception as e:
            print(f"❌ Email login test failed: {str(e)}")
        
        # Test 2: Login with roll number
        print("\n🧪 Test 2: Login with roll number")
        try:
            login_data = UserLogin(email=test_roll_number, password=test_password)
            response = await login_user(login_data)
            
            if response["success"]:
                print(f"✅ Roll number login successful!")
                print(f"   User: {response['user']['name']} ({response['user']['email']})")
                print(f"   Role: {response['user']['role']}")
                print(f"   Roll Number: {response['user'].get('roll_number', 'N/A')}")
            else:
                print(f"❌ Roll number login failed: {response.get('message', 'Unknown error')}")
        except Exception as e:
            print(f"❌ Roll number login test failed: {str(e)}")
        
        # Test 3: Login with wrong password
        print("\n🧪 Test 3: Login with wrong password")
        try:
            login_data = UserLogin(email=test_email, password="wrongpassword")
            response = await login_user(login_data)
            print(f"❌ Login should have failed but succeeded: {response}")
        except Exception as e:
            print(f"✅ Correctly rejected wrong password: {str(e)}")
        
        # Clean up test data
        await db.users.delete_one({"_id": student_id})
        print(f"\n🧹 Cleaned up test student")
        
        print(f"\n✅ All login tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Login test failed: {str(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    asyncio.run(test_login())
