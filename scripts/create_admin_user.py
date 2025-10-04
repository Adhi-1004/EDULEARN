#!/usr/bin/env python3
"""
Script to create admin user for modLRN
"""
import asyncio
import sys
import os
sys.path.append('backend')

from backend.app.db.mock_db import mock_db
from backend.app.models.models import UserModel
from backend.app.utils.auth_utils import create_access_token

async def create_admin_user():
    """Create admin user with proper credentials"""
    print("🔧 Creating admin user...")
    
    # Clear existing users to start fresh
    mock_db.data['users'] = []
    print("🧹 Cleared existing users")
    
    # Create admin user
    admin_user = {
        "username": "Adhithya",
        "email": "adhiadmin@gmail.com",
        "password": UserModel.hash_password("admin123"),  # Hash the password
        "is_admin": True,
        "role": "admin",
        "name": "Adhithya Admin",
        "profile_picture": None,
        "face_descriptor": None,
        # Gamification fields
        "xp": 0,
        "level": 1,
        "streak": 0,
        "longest_streak": 0,
        "badges": [],
        "last_activity": None,
        "total_questions_answered": 0,
        "correct_answers": 0,
        "perfect_scores": 0,
        "consecutive_days": 0
    }
    
    # Insert admin user
    result = await mock_db.insert_one(admin_user)
    admin_user['_id'] = result['inserted_id']
    
    print(f"✅ Admin user created successfully!")
    print(f"   Username: Adhithya")
    print(f"   Email: adhiadmin@gmail.com")
    print(f"   Password: admin123")
    print(f"   Role: admin")
    print(f"   User ID: {admin_user['_id']}")
    
    # Test login
    print("\n🔐 Testing admin login...")
    test_user = await mock_db.find_one({"email": "adhiadmin@gmail.com"})
    if test_user:
        password_valid = UserModel.verify_password("admin123", test_user["password"])
        if password_valid:
            print("✅ Password verification successful!")
            
            # Create access token
            access_token = create_access_token(
                data={
                    "sub": str(test_user["_id"]),
                    "email": test_user["email"],
                    "role": test_user.get("role", "admin")
                }
            )
            print(f"✅ Access token created successfully!")
            print(f"   Token: {access_token[:50]}...")
        else:
            print("❌ Password verification failed!")
    else:
        print("❌ Admin user not found!")
    
    print("\n🎯 Admin user setup complete!")
    print("You can now login with:")
    print("   Email: adhiadmin@gmail.com")
    print("   Password: admin123")

if __name__ == "__main__":
    asyncio.run(create_admin_user())
