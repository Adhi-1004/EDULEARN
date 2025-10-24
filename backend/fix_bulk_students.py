#!/usr/bin/env python3
"""
Migration script to fix existing bulk uploaded students
"""
import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.db import init_db, get_db
from app.models.models import UserModel

async def fix_existing_students():
    """Fix existing bulk uploaded students with incorrect password hashes"""
    print("Fixing existing bulk uploaded students...")
    
    try:
        # Initialize database
        await init_db()
        db = await get_db()
        
        # Find all students created by bulk upload
        bulk_students = await db.users.find({
            "created_by": "bulk_upload",
            "role": "student"
        }).to_list(length=None)
        
        print(f"📊 Found {len(bulk_students)} bulk uploaded students")
        
        fixed_count = 0
        
        for student in bulk_students:
            try:
                email = student.get('email', '')
                roll_number = student.get('roll_number', '')
                
                if not email or not roll_number:
                    print(f"⚠️  Skipping student {student.get('_id')} - missing email or roll number")
                    continue
                
                # Re-hash password using UserModel method
                new_password_hash = UserModel.hash_password(roll_number)
                
                # Update the student with correct password hash
                result = await db.users.update_one(
                    {"_id": student["_id"]},
                    {"$set": {"password_hash": new_password_hash}}
                )
                
                if result.modified_count > 0:
                    print(f"✅ Fixed password for {email} ({roll_number})")
                    fixed_count += 1
                else:
                    print(f"⚠️  No changes needed for {email}")
                    
            except Exception as e:
                print(f"❌ Error fixing student {student.get('email', 'unknown')}: {str(e)}")
        
        print(f"\n✅ Migration complete! Fixed {fixed_count} students")
        
        # Test login for a few students
        print(f"\n🧪 Testing login for fixed students...")
        test_students = bulk_students[:3]  # Test first 3
        
        for student in test_students:
            email = student.get('email', '')
            roll_number = student.get('roll_number', '')
            
            if email and roll_number:
                # Test password verification
                password_hash = student.get('password_hash', '')
                is_valid = UserModel.verify_password(roll_number, password_hash)
                print(f"   {email}: Password verification = {is_valid}")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    asyncio.run(fix_existing_students())
