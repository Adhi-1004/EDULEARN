#!/usr/bin/env python3
"""
Create a test student and verify login works
"""
import asyncio
import sys
import os
from bson import ObjectId

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.db import init_db, get_db
from app.models.models import UserModel
from app.api.auth import login_user
from app.schemas.schemas import UserLogin

async def create_and_test_student():
    """Create a test student and verify login works"""
    print("Creating and testing student login...")
    
    try:
        # Initialize database
        await init_db()
        db = await get_db()
        
        # Test student data
        test_email = "teststudent@example.com"
        test_roll_number = "TEST001"
        test_password = test_roll_number
        
        # Clean up any existing test student
        await db.users.delete_many({"email": test_email})
        
        # Create password hash using UserModel method
        password_hash = UserModel.hash_password(test_password)
        print(f"✅ Created password hash: {password_hash[:30]}...")
        
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
        
        # Insert student
        result = await db.users.insert_one(student_doc)
        student_id = result.inserted_id
        print(f"✅ Created test student with ID: {student_id}")
        
        # Test login with email
        print(f"\n🧪 Testing login with email...")
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
        
        # Test login with roll number
        print(f"\n🧪 Testing login with roll number...")
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
        
        # Clean up test data
        await db.users.delete_one({"_id": student_id})
        print(f"\n🧹 Cleaned up test student")
        
        print(f"\n✅ Student creation and login test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    asyncio.run(create_and_test_student())
