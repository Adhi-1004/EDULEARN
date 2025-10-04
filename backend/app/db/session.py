"""
Database session management
"""
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from datetime import datetime

from ..core.config import settings

# Database connection
client = None
db = None

async def init_db():
    """Initialize database connection"""
    global client, db
    try:
        print(f"[DB] Connecting to MongoDB...")
        print(f"   - URI: {settings.mongo_uri[:50]}..." if len(settings.mongo_uri) > 50 else f"   - URI: {settings.mongo_uri}")
        print(f"   - Database: {settings.db_name}")
        
        # Add connection pooling and timeout settings
        client = AsyncIOMotorClient(
            settings.mongo_uri,
            maxPoolSize=10,
            minPoolSize=1,
            maxIdleTimeMS=30000,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            socketTimeoutMS=20000
        )
        db = client[settings.db_name]
        
        # Test the connection
        print(f"[DB] Testing connection...")
        await client.admin.command('ping')
        
        # Create indexes for new collections
        print(f"[DB] Creating indexes for new collections...")
        try:
            # Batches collection indexes
            await db.batches.create_index([("teacher_id", 1)])
            await db.batches.create_index([("name", 1)])
            
            # Assessments collection indexes
            await db.assessments.create_index([("created_by", 1)])
            await db.assessments.create_index([("topic", 1)])
            
            # Coding problems collection indexes
            await db.coding_problems.create_index([("topic", 1)])
            await db.coding_problems.create_index([("difficulty", 1)])
            await db.coding_problems.create_index([("created_at", -1)])
            
            print(f"[DB] Database indexes created successfully")
        except Exception as index_error:
            print(f"[DB] Warning: Failed to create indexes: {str(index_error)}")
        
        # Seed database with sample coding problems if none exist
        await seed_sample_coding_problems(db)
        
        print(f"[DB] MongoDB Connected Successfully")
        return db
    except Exception as e:
        print(f"[DB] MongoDB Connection Error: {str(e)}")
        print(f"[DB] Error type: {type(e).__name__}")
        import traceback
        print(f"[DB] Connection traceback: {traceback.format_exc()}")
        raise e

async def get_db():
    """Get database instance with retry logic"""
    global db, client
    max_retries = 3
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            if db is None:
                print(f"[DB] Initializing database connection (attempt {attempt + 1}/{max_retries})")
                await init_db()
            else:
                print(f"[DB] Testing existing database connection (attempt {attempt + 1}/{max_retries})")
            
            # Test connection before returning
            try:
                await client.admin.command('ping')
                print(f"[DB] Database connection test successful")
                return db
            except Exception as ping_error:
                print(f"[DB] Database ping failed (attempt {attempt + 1}/{max_retries}): {str(ping_error)}")
                if attempt < max_retries - 1:
                    print(f"[DB] Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                else:
                    print(f"[DB] All retry attempts failed, reinitializing connection")
                    # Force reinitialization on final attempt
                    db = None
                    client = None
                    await init_db()
                    return db
                    
        except Exception as e:
            print(f"[DB] Database connection attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                print(f"[DB] Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
                continue
            else:
                print(f"[DB] All retry attempts failed")
                raise Exception(f"Database connection failed after {max_retries} attempts: {str(e)}")
    
    # This should never be reached, but just in case
    raise Exception("Database connection failed - unexpected error")

async def seed_sample_coding_problems(db):
    """Seed database with sample coding problems if none exist"""
    try:
        # Check if any coding problems exist
        existing_count = await db.coding_problems.count_documents({})
        if existing_count > 0:
            print(f"[SEED] Coding problems already exist ({existing_count} problems), skipping seed")
            return
        
        print(f"[SEED] No coding problems found, seeding sample problems...")
        
        sample_problems = [
            {
                "title": "Two Sum",
                "description": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
                "topic": "Arrays",
                "difficulty": "easy",
                "constraints": ["2 <= nums.length <= 10^4", "-10^9 <= nums[i] <= 10^9", "-10^9 <= target <= 10^9"],
                "examples": [
                    {
                        "input": {"nums": [2, 7, 11, 15], "target": 9},
                        "output": [0, 1],
                        "explanation": "Because nums[0] + nums[1] == 9, we return [0, 1]."
                    }
                ],
                "test_cases": [
                    {"input": {"nums": [2, 7, 11, 15], "target": 9}, "output": [0, 1]},
                    {"input": {"nums": [3, 2, 4], "target": 6}, "output": [1, 2]},
                    {"input": {"nums": [3, 3], "target": 6}, "output": [0, 1]}
                ],
                "hidden_test_cases": [
                    {"input": {"nums": [1, 2, 3, 4, 5], "target": 8}, "output": [2, 4]},
                    {"input": {"nums": [-1, -2, -3, -4, -5], "target": -8}, "output": [2, 4]}
                ],
                "expected_complexity": {"time": "O(n)", "space": "O(n)"},
                "hints": [
                    "Use a hash map to store numbers and their indices",
                    "For each number, check if target - number exists in the map"
                ],
                "tags": ["arrays", "hash-table", "easy"],
                "created_by": "AI",
                "created_at": datetime.utcnow(),
                "success_rate": 0.0,
                "average_time": None
            },
            {
                "title": "Maximum Subarray Sum (Kadane's Algorithm)",
                "description": "Given an integer array nums, find the contiguous subarray (containing at least one number) which has the largest sum and return its sum.",
                "topic": "Arrays",
                "difficulty": "medium",
                "constraints": ["1 <= nums.length <= 10^5", "-10^4 <= nums[i] <= 10^4"],
                "examples": [
                    {
                        "input": {"nums": [-2, 1, -3, 4, -1, 2, 1, -5, 4]},
                        "output": 6,
                        "explanation": "The subarray [4,-1,2,1] has the largest sum 6."
                    }
                ],
                "test_cases": [
                    {"input": {"nums": [-2, 1, -3, 4, -1, 2, 1, -5, 4]}, "output": 6},
                    {"input": {"nums": [1]}, "output": 1},
                    {"input": {"nums": [5, 4, -1, 7, 8]}, "output": 23}
                ],
                "hidden_test_cases": [
                    {"input": {"nums": [-1, -2, -3, -4]}, "output": -1},
                    {"input": {"nums": [1, 2, 3, 4, 5]}, "output": 15}
                ],
                "expected_complexity": {"time": "O(n)", "space": "O(1)"},
                "hints": [
                    "Use Kadane's algorithm",
                    "Keep track of the maximum sum ending at each position",
                    "If the current sum becomes negative, reset it to 0"
                ],
                "tags": ["arrays", "dynamic-programming", "medium"],
                "created_by": "AI",
                "created_at": datetime.utcnow(),
                "success_rate": 0.0,
                "average_time": None
            },
            {
                "title": "Binary Search",
                "description": "Given an array of integers nums which is sorted in ascending order, and an integer target, write a function to search target in nums. If target exists, then return its index. Otherwise, return -1.",
                "topic": "Arrays",
                "difficulty": "easy",
                "constraints": ["1 <= nums.length <= 10^4", "-10^4 < nums[i], target < 10^4", "All integers in nums are unique", "nums is sorted in ascending order"],
                "examples": [
                    {
                        "input": {"nums": [-1, 0, 3, 5, 9, 12], "target": 9},
                        "output": 4,
                        "explanation": "9 exists in nums and its index is 4"
                    }
                ],
                "test_cases": [
                    {"input": {"nums": [-1, 0, 3, 5, 9, 12], "target": 9}, "output": 4},
                    {"input": {"nums": [-1, 0, 3, 5, 9, 12], "target": 2}, "output": -1},
                    {"input": {"nums": [5], "target": 5}, "output": 0}
                ],
                "hidden_test_cases": [
                    {"input": {"nums": [1, 2, 3, 4, 5], "target": 3}, "output": 2},
                    {"input": {"nums": [1, 2, 3, 4, 5], "target": 6}, "output": -1}
                ],
                "expected_complexity": {"time": "O(log n)", "space": "O(1)"},
                "hints": [
                    "Use binary search algorithm",
                    "Compare target with middle element",
                    "Eliminate half of the search space in each iteration"
                ],
                "tags": ["arrays", "binary-search", "easy"],
                "created_by": "AI",
                "created_at": datetime.utcnow(),
                "success_rate": 0.0,
                "average_time": None
            }
        ]
        
        # Insert sample problems
        result = await db.coding_problems.insert_many(sample_problems)
        print(f"[SEED] Successfully seeded {len(result.inserted_ids)} sample coding problems")
        
    except Exception as e:
        print(f"[SEED] Error seeding sample coding problems: {str(e)}")

async def close_db():
    """Close database connection"""
    global client
    if client:
        client.close()
        print("[CLOSE] MongoDB Connection Closed")