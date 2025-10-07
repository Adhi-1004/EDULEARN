#!/usr/bin/env python3
"""
Setup test users in MongoDB
"""
import asyncio
import bcrypt
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

async def setup_test_users():
    """Setup test users in MongoDB"""
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient("mongodb://127.0.0.1:27017/edulearn")
        db = client.edulearn
        
        print("Connecting to MongoDB...")
        
        # Generate password hash
        password = "password123"
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        
        # Test users
        test_users = [
            {
                "_id": ObjectId(),
                "email": "test@example.com",
                "username": "testuser",
                "name": "Test User",
                "password_hash": password_hash,
                "role": "student",
                "is_admin": False,
                "created_at": "2024-01-01T00:00:00Z"
            },
            {
                "_id": ObjectId(),
                "email": "teacher@example.com",
                "username": "teacher",
                "name": "Test Teacher",
                "password_hash": password_hash,
                "role": "teacher",
                "is_admin": False,
                "created_at": "2024-01-01T00:00:00Z"
            }
        ]
        
        # Clear existing test users
        await db.users.delete_many({"email": {"$in": ["test@example.com", "teacher@example.com"]}})
        
        # Insert test users
        result = await db.users.insert_many(test_users)
        print(f"Inserted {len(result.inserted_ids)} test users")
        
        # Create test batch
        batch = {
            "_id": ObjectId(),
            "name": "Computer Science Batch A",
            "student_ids": [str(test_users[0]["_id"])],
            "created_at": "2024-01-01T00:00:00Z"
        }
        
        await db.batches.delete_many({"name": "Computer Science Batch A"})
        await db.batches.insert_one(batch)
        print("Created test batch")
        
        # Create test teacher assessment
        assessment = {
            "_id": ObjectId(),
            "title": "Python Programming Basics",
            "topic": "Python",
            "difficulty": "easy",
            "question_count": 5,
            "questions": [
                {
                    "question": "What is the correct way to declare a variable in Python?",
                    "options": ["var x = 5", "x = 5", "int x = 5", "declare x = 5"],
                    "correct_answer": 1,
                    "explanation": "In Python, variables are declared by simply assigning a value."
                }
            ],
            "batches": [str(batch["_id"])],
            "teacher_id": str(test_users[1]["_id"]),
            "type": "mcq",
            "created_at": "2024-01-01T00:00:00Z",
            "is_active": True,
            "status": "published"
        }
        
        await db.teacher_assessments.delete_many({"title": "Python Programming Basics"})
        await db.teacher_assessments.insert_one(assessment)
        print("Created test teacher assessment")
        
        print("Test data setup complete!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(setup_test_users())

