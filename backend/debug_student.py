#!/usr/bin/env python3
"""
Debug script to check student data in database
"""
import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.db import init_db, get_db
from app.models.models import UserModel

async def debug_student():
    """Debug student data in database"""
    print("Debugging student data in database...")
    
    try:
        # Initialize database
        await init_db()
        db = await get_db()
        
        # Check for student23
        student = await db.users.find_one({"email": "student23@gmail.com"})
        
        if student:
            print(f"✅ Found student23 in users collection:")
            print(f"   ID: {student['_id']}")
            print(f"   Email: {student['email']}")
            print(f"   Username: {student.get('username', 'N/A')}")
            print(f"   Roll Number: {student.get('roll_number', 'N/A')}")
            print(f"   Full Name: {student.get('full_name', 'N/A')}")
            print(f"   Role: {student.get('role', 'N/A')}")
            print(f"   Batch ID: {student.get('batch_id', 'N/A')}")
            print(f"   Password Hash: {student.get('password_hash', 'N/A')[:30]}...")
            print(f"   Created By: {student.get('created_by', 'N/A')}")
            print(f"   Login Method: {student.get('login_method', 'N/A')}")
            print(f"   Is Active: {student.get('is_active', 'N/A')}")
            
            # Test password verification
            print(f"\n🧪 Testing password verification:")
            roll_number = student.get('roll_number', 'student23')
            password_hash = student.get('password_hash', '')
            
            print(f"   Roll Number: {roll_number}")
            print(f"   Password Hash: {password_hash[:30]}...")
            
            # Test with roll number as password
            is_valid = UserModel.verify_password(roll_number, password_hash)
            print(f"   Password verification (roll_number): {is_valid}")
            
            # Test with 'student23' as password
            is_valid2 = UserModel.verify_password('student23', password_hash)
            print(f"   Password verification ('student23'): {is_valid2}")
            
        else:
            print(f"❌ student23 not found in users collection")
            
            # Check bulk_uploads collection
            print(f"\n🔍 Checking bulk_uploads collection...")
            bulk_uploads = await db.bulk_uploads.find({}).to_list(length=None)
            
            for upload in bulk_uploads:
                print(f"   Upload ID: {upload['_id']}")
                print(f"   Batch ID: {upload.get('batch_id', 'N/A')}")
                print(f"   Created Students: {len(upload.get('created_students', []))}")
                
                for student_data in upload.get('created_students', []):
                    if student_data.get('email') == 'student23@gmail.com':
                        print(f"   ✅ Found student23 in bulk_uploads:")
                        print(f"      Name: {student_data.get('name', 'N/A')}")
                        print(f"      Email: {student_data.get('email', 'N/A')}")
                        print(f"      Roll Number: {student_data.get('roll_number', 'N/A')}")
                        print(f"      Row: {student_data.get('row', 'N/A')}")
                        break
        
        # Check all students in users collection
        print(f"\n📊 All students in users collection:")
        all_students = await db.users.find({"role": "student"}).to_list(length=None)
        print(f"   Total students: {len(all_students)}")
        
        for student in all_students[:5]:  # Show first 5
            print(f"   - {student.get('email', 'N/A')} ({student.get('roll_number', 'N/A')}) - {student.get('created_by', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Debug failed: {str(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    asyncio.run(debug_student())
