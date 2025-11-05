"""
Database Initialization Script
Creates all necessary indexes and optimizes the database for production
"""
import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from app.services.database_optimization_service import DatabaseOptimizationService
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def initialize_database():
    """Initialize the database with all necessary indexes and optimizations"""
    logger.info("🚀 Starting database initialization...")
    
    try:
        # Initialize MongoDB client
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = client[settings.DATABASE_NAME]
        
        # Create optimization service
        optimization_service = DatabaseOptimizationService(db)
        
        # Create all indexes
        await optimization_service.create_all_indexes()
        
        # Get index statistics
        stats = await optimization_service.get_index_stats()
        logger.info("📊 Index Statistics:")
        for collection, stat in stats.items():
            if "error" not in stat:
                logger.info(f"  {collection}: {stat['index_count']} indexes")
            else:
                logger.warning(f"  {collection}: Error - {stat['error']}")
        
        # Test query performance
        await test_query_performance(optimization_service)
        
        logger.info("✅ Database initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise
    finally:
        # Close client
        client.close()

async def test_query_performance(optimization_service: DatabaseOptimizationService):
    """Test query performance for common operations"""
    logger.info("🧪 Testing query performance...")
    
    # Test common queries
    test_queries = [
        {
            "collection": "users",
            "query": {"role": "student", "is_active": True},
            "description": "Active students"
        },
        {
            "collection": "assessments",
            "query": {"created_by": "test_teacher", "is_active": True},
            "description": "Teacher's active assessments"
        },
        {
            "collection": "submissions",
            "query": {"student_id": "test_student", "status": "submitted"},
            "description": "Student's submitted assessments"
        },
        {
            "collection": "batches",
            "query": {"created_by": "test_teacher", "is_active": True},
            "description": "Teacher's active batches"
        }
    ]
    
    for test_query in test_queries:
        try:
            result = await optimization_service.analyze_query_performance(
                test_query["collection"],
                test_query["query"]
            )
            
            if "error" not in result:
                logger.info(f"  {test_query['description']}: {result['execution_time_ms']}ms")
            else:
                logger.warning(f"  {test_query['description']}: Error - {result['error']}")
                
        except Exception as e:
            logger.warning(f"  {test_query['description']}: Failed to test - {e}")

async def create_sample_data():
    """Create sample data for testing"""
    logger.info("📝 Creating sample data...")
    
    try:
        # Initialize MongoDB client
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = client[settings.DATABASE_NAME]
        
        # Create sample users
        users_collection = db.users
        sample_users = [
            {
                "username": "admin",
                "email": "admin@edulearn.com",
                "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J8K8K8K8K",
                "role": "admin",
                "is_active": True
            },
            {
                "username": "teacher1",
                "email": "teacher1@edulearn.com",
                "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J8K8K8K8K",
                "role": "teacher",
                "is_active": True
            },
            {
                "username": "student1",
                "email": "student1@edulearn.com",
                "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J8K8K8K8K",
                "role": "student",
                "is_active": True
            }
        ]
        
        # Insert sample users
        await users_collection.insert_many(sample_users)
        logger.info("✅ Sample users created")
        
        # Create sample batch
        batches_collection = db.batches
        sample_batch = {
            "name": "Sample Batch 2024",
            "description": "A sample batch for testing",
            "created_by": "teacher1",
            "student_ids": ["student1"],
            "total_students": 1,
            "is_active": True
        }
        
        await batches_collection.insert_one(sample_batch)
        logger.info("✅ Sample batch created")
        
        # Create sample assessment
        assessments_collection = db.assessments
        sample_assessment = {
            "title": "Sample Assessment",
            "description": "A sample assessment for testing",
            "subject": "Mathematics",
            "topic": "Algebra",
            "difficulty": "medium",
            "type": "mcq",
            "status": "published",
            "total_questions": 5,
            "total_points": 10,
            "config": {
                "time_limit": 30,
                "max_attempts": 1,
                "shuffle_questions": True,
                "shuffle_options": True,
                "show_correct_answers": False,
                "show_explanations": False,
                "allow_review": True,
                "auto_submit": False,
                "proctoring_enabled": False
            },
            "schedule": {
                "start_date": None,
                "end_date": None,
                "duration": 30,
                "timezone": "UTC",
                "is_scheduled": False
            },
            "assigned_batches": ["sample_batch_id"],
            "assigned_students": [],
            "access_control": {},
            "created_by": "teacher1",
            "is_active": True,
            "questions": [
                {
                    "id": "q_1",
                    "type": "multiple_choice",
                    "question_text": "What is 2 + 2?",
                    "options": [
                        {"id": "opt_1", "text": "3", "is_correct": False},
                        {"id": "opt_2", "text": "4", "is_correct": True},
                        {"id": "opt_3", "text": "5", "is_correct": False},
                        {"id": "opt_4", "text": "6", "is_correct": False}
                    ],
                    "correct_answer": 1,
                    "explanation": "2 + 2 = 4",
                    "points": 2,
                    "difficulty": "easy",
                    "tags": ["basic", "arithmetic"],
                    "metadata": {}
                }
            ],
            "analytics": {
                "total_attempts": 0,
                "average_score": 0.0,
                "completion_rate": 0.0,
                "average_time": 0.0,
                "difficulty_distribution": {},
                "question_analytics": {},
                "last_updated": "2024-01-01T00:00:00Z"
            },
            "tags": ["sample", "test"],
            "metadata": {}
        }
        
        await assessments_collection.insert_one(sample_assessment)
        logger.info("✅ Sample assessment created")
        
        logger.info("✅ Sample data creation completed!")
        
    except Exception as e:
        logger.error(f"❌ Sample data creation failed: {e}")
        raise
    finally:
        # Close client
        client.close()

async def main():
    """Main function to run database initialization"""
    try:
        # Initialize database with indexes
        await initialize_database()
        
        # Create sample data
        await create_sample_data()
        
        logger.info("🎉 Database initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())
