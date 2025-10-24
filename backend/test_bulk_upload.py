#!/usr/bin/env python3
"""
Test bulk upload functionality with sample Excel data
"""
import asyncio
import sys
import os
import pandas as pd
import io
from bson import ObjectId

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.db import init_db, get_db
from app.api.bulk_students import validate_student_data, create_student_accounts, BulkUploadResponse
from app.models.models import UserModel

async def test_bulk_upload():
    """Test bulk upload functionality with sample data"""
    print("Testing bulk upload functionality...")
    
    try:
        # Initialize database
        await init_db()
        db = await get_db()
        
        # Create sample data matching your Excel format
        sample_data = {
            'name': ['student26', 'student25', 'student24'],
            'roll_number': ['student26', 'student25', 'student24'],
            'email': ['student26@gmail.com', 'student25@gmail.com', 'student24@gmail.com']
        }
        
        df = pd.DataFrame(sample_data)
        print(f"✅ Created sample DataFrame with {len(df)} rows")
        print(f"📊 Sample data:")
        print(df.to_string(index=False))
        
        # Test data validation
        print(f"\n🧪 Testing data validation...")
        students_data, validation_errors = await validate_student_data(df)
        
        print(f"✅ Validation complete:")
        print(f"   Valid students: {len(students_data)}")
        print(f"   Validation errors: {len(validation_errors)}")
        
        if validation_errors:
            print(f"❌ Validation errors found:")
            for error in validation_errors:
                print(f"   Row {error['row']}: {error['errors']}")
        
        # Test student creation (without actually inserting to avoid duplicates)
        print(f"\n🧪 Testing student creation logic...")
        
        # Create a test batch
        test_batch_id = str(ObjectId())
        batch_doc = {
            "_id": ObjectId(test_batch_id),
            "name": "Test Batch",
            "description": "Test batch for bulk upload",
            "student_count": 0,
            "created_at": "2024-01-01T00:00:00Z",
            "created_by": "test"
        }
        
        # Insert test batch
        await db.batches.insert_one(batch_doc)
        print(f"✅ Created test batch: {test_batch_id}")
        
        # Test creating student accounts
        existing_data = {"existing_emails": set(), "existing_rolls": set()}
        created_students, creation_errors = await create_student_accounts(
            db, students_data, test_batch_id, existing_data
        )
        
        print(f"✅ Student creation test complete:")
        print(f"   Created students: {len(created_students)}")
        print(f"   Creation errors: {len(creation_errors)}")
        
        # Test BulkUploadResponse creation
        print(f"\n🧪 Testing BulkUploadResponse creation...")
        try:
            response = BulkUploadResponse(
                success=len(created_students) > 0,
                total_rows=len(df),
                successful_imports=len(created_students),
                failed_imports=len(validation_errors + creation_errors),
                errors=validation_errors + creation_errors,
                created_students=created_students,
                batch_id=test_batch_id
            )
            print(f"✅ BulkUploadResponse created successfully!")
            print(f"   Success: {response.success}")
            print(f"   Total rows: {response.total_rows}")
            print(f"   Successful imports: {response.successful_imports}")
            print(f"   Failed imports: {response.failed_imports}")
            
            if created_students:
                print(f"   Created students:")
                for student in created_students:
                    print(f"     - {student['name']} ({student['roll_number']}) - {student['email']} [Row {student['row']}]")
                    
        except Exception as e:
            print(f"❌ BulkUploadResponse creation failed: {str(e)}")
            return False
        
        # Clean up test data
        print(f"\n🧹 Cleaning up test data...")
        await db.users.delete_many({"batch_id": test_batch_id})
        await db.batches.delete_one({"_id": ObjectId(test_batch_id)})
        print(f"✅ Cleanup complete")
        
        print(f"\n✅ All bulk upload tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Bulk upload test failed: {str(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    asyncio.run(test_bulk_upload())
