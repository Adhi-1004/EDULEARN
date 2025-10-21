"""
Database Optimization Service
Service for managing database indexes and performance optimization
"""
import asyncio
from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import IndexModel, ASCENDING, DESCENDING, TEXT, HASHED
import logging

logger = logging.getLogger(__name__)

class DatabaseOptimizationService:
    """Service for database optimization and index management"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def create_all_indexes(self):
        """Create all necessary indexes for optimal performance"""
        logger.info("🚀 Starting database index creation...")
        
        try:
            await self._create_user_indexes()
            await self._create_assessment_indexes()
            await self._create_submission_indexes()
            await self._create_batch_indexes()
            await self._create_notification_indexes()
            await self._create_coding_indexes()
            await self._create_analytics_indexes()
            
            logger.info("✅ All database indexes created successfully!")
            
        except Exception as e:
            logger.error(f"❌ Failed to create database indexes: {e}")
            raise
    
    async def _create_user_indexes(self):
        """Create indexes for users collection"""
        logger.info("📊 Creating user indexes...")
        
        collection = self.db.users
        
        # Email index (unique)
        await collection.create_index("email", unique=True)
        
        # Username index (unique)
        await collection.create_index("username", unique=True)
        
        # Role index
        await collection.create_index("role")
        
        # Active status index
        await collection.create_index("is_active")
        
        # Created at index
        await collection.create_index("created_at")
        
        # Last login index
        await collection.create_index("last_login")
        
        # Compound indexes
        await collection.create_index([
            ("role", ASCENDING),
            ("is_active", ASCENDING)
        ])
        
        await collection.create_index([
            ("created_at", DESCENDING),
            ("is_active", ASCENDING)
        ])
        
        logger.info("✅ User indexes created")
    
    async def _create_assessment_indexes(self):
        """Create indexes for assessments collection"""
        logger.info("📊 Creating assessment indexes...")
        
        collection = self.db.assessments
        
        # Title index
        await collection.create_index("title")
        
        # Subject index
        await collection.create_index("subject")
        
        # Topic index
        await collection.create_index("topic")
        
        # Difficulty index
        await collection.create_index("difficulty")
        
        # Type index
        await collection.create_index("type")
        
        # Status index
        await collection.create_index("status")
        
        # Created by index
        await collection.create_index("created_by")
        
        # Created at index
        await collection.create_index("created_at")
        
        # Published at index
        await collection.create_index("published_at")
        
        # Is active index
        await collection.create_index("is_active")
        
        # Assigned batches index
        await collection.create_index("assigned_batches")
        
        # Assigned students index
        await collection.create_index("assigned_students")
        
        # Text search index
        await collection.create_index([
            ("title", TEXT),
            ("description", TEXT),
            ("subject", TEXT),
            ("topic", TEXT)
        ])
        
        # Compound indexes
        await collection.create_index([
            ("created_by", ASCENDING),
            ("is_active", ASCENDING),
            ("created_at", DESCENDING)
        ])
        
        await collection.create_index([
            ("status", ASCENDING),
            ("is_active", ASCENDING),
            ("published_at", DESCENDING)
        ])
        
        await collection.create_index([
            ("subject", ASCENDING),
            ("difficulty", ASCENDING),
            ("is_active", ASCENDING)
        ])
        
        await collection.create_index([
            ("assigned_batches", ASCENDING),
            ("status", ASCENDING),
            ("is_active", ASCENDING)
        ])
        
        logger.info("✅ Assessment indexes created")
    
    async def _create_submission_indexes(self):
        """Create indexes for submissions collection"""
        logger.info("📊 Creating submission indexes...")
        
        collection = self.db.submissions
        
        # Assessment ID index
        await collection.create_index("assessment_id")
        
        # Student ID index
        await collection.create_index("student_id")
        
        # Batch ID index
        await collection.create_index("batch_id")
        
        # Status index
        await collection.create_index("status")
        
        # Started at index
        await collection.create_index("started_at")
        
        # Submitted at index
        await collection.create_index("submitted_at")
        
        # Attempt number index
        await collection.create_index("attempt_number")
        
        # Total score index
        await collection.create_index("total_score")
        
        # Percentage index
        await collection.create_index("percentage")
        
        # Compound indexes
        await collection.create_index([
            ("assessment_id", ASCENDING),
            ("student_id", ASCENDING),
            ("attempt_number", ASCENDING)
        ])
        
        await collection.create_index([
            ("student_id", ASCENDING),
            ("submitted_at", DESCENDING)
        ])
        
        await collection.create_index([
            ("batch_id", ASCENDING),
            ("submitted_at", DESCENDING)
        ])
        
        await collection.create_index([
            ("assessment_id", ASCENDING),
            ("status", ASCENDING),
            ("submitted_at", DESCENDING)
        ])
        
        await collection.create_index([
            ("student_id", ASCENDING),
            ("assessment_id", ASCENDING),
            ("status", ASCENDING)
        ])
        
        logger.info("✅ Submission indexes created")
    
    async def _create_batch_indexes(self):
        """Create indexes for batches collection"""
        logger.info("📊 Creating batch indexes...")
        
        collection = self.db.batches
        
        # Name index
        await collection.create_index("name")
        
        # Created by index
        await collection.create_index("created_by")
        
        # Created at index
        await collection.create_index("created_at")
        
        # Is active index
        await collection.create_index("is_active")
        
        # Student IDs index
        await collection.create_index("student_ids")
        
        # Total students index
        await collection.create_index("total_students")
        
        # Compound indexes
        await collection.create_index([
            ("created_by", ASCENDING),
            ("is_active", ASCENDING),
            ("created_at", DESCENDING)
        ])
        
        await collection.create_index([
            ("is_active", ASCENDING),
            ("total_students", DESCENDING)
        ])
        
        logger.info("✅ Batch indexes created")
    
    async def _create_notification_indexes(self):
        """Create indexes for notifications collection"""
        logger.info("📊 Creating notification indexes...")
        
        collection = self.db.notifications
        
        # User ID index
        await collection.create_index("user_id")
        
        # Type index
        await collection.create_index("type")
        
        # Priority index
        await collection.create_index("priority")
        
        # Is read index
        await collection.create_index("is_read")
        
        # Created at index
        await collection.create_index("created_at")
        
        # Read at index
        await collection.create_index("read_at")
        
        # Assessment ID index
        await collection.create_index("assessment_id")
        
        # Batch ID index
        await collection.create_index("batch_id")
        
        # Compound indexes
        await collection.create_index([
            ("user_id", ASCENDING),
            ("is_read", ASCENDING),
            ("created_at", DESCENDING)
        ])
        
        await collection.create_index([
            ("user_id", ASCENDING),
            ("type", ASCENDING),
            ("created_at", DESCENDING)
        ])
        
        await collection.create_index([
            ("user_id", ASCENDING),
            ("priority", ASCENDING),
            ("is_read", ASCENDING)
        ])
        
        logger.info("✅ Notification indexes created")
    
    async def _create_coding_indexes(self):
        """Create indexes for coding-related collections"""
        logger.info("📊 Creating coding indexes...")
        
        # Coding problems collection
        problems_collection = self.db.coding_problems
        
        await problems_collection.create_index("title")
        await problems_collection.create_index("difficulty")
        await problems_collection.create_index("language")
        await problems_collection.create_index("created_by")
        await problems_collection.create_index("created_at")
        await problems_collection.create_index("is_active")
        
        # Text search for problems
        await problems_collection.create_index([
            ("title", TEXT),
            ("description", TEXT)
        ])
        
        # Coding solutions collection
        solutions_collection = self.db.coding_solutions
        
        await solutions_collection.create_index("problem_id")
        await solutions_collection.create_index("student_id")
        await solutions_collection.create_index("language")
        await solutions_collection.create_index("status")
        await solutions_collection.create_index("submitted_at")
        await solutions_collection.create_index("score")
        
        # Compound indexes for solutions
        await solutions_collection.create_index([
            ("problem_id", ASCENDING),
            ("student_id", ASCENDING),
            ("submitted_at", DESCENDING)
        ])
        
        await solutions_collection.create_index([
            ("student_id", ASCENDING),
            ("submitted_at", DESCENDING)
        ])
        
        # Coding sessions collection
        sessions_collection = self.db.coding_sessions
        
        await sessions_collection.create_index("problem_id")
        await sessions_collection.create_index("student_id")
        await sessions_collection.create_index("language")
        await sessions_collection.create_index("started_at")
        await sessions_collection.create_index("is_active")
        
        # Compound indexes for sessions
        await sessions_collection.create_index([
            ("student_id", ASCENDING),
            ("is_active", ASCENDING),
            ("started_at", DESCENDING)
        ])
        
        logger.info("✅ Coding indexes created")
    
    async def _create_analytics_indexes(self):
        """Create indexes for analytics collections"""
        logger.info("📊 Creating analytics indexes...")
        
        # User analytics collection
        user_analytics_collection = self.db.user_analytics
        
        await user_analytics_collection.create_index("user_id")
        await user_analytics_collection.create_index("last_updated")
        
        # Assessment analytics collection
        assessment_analytics_collection = self.db.assessment_analytics
        
        await assessment_analytics_collection.create_index("assessment_id")
        await assessment_analytics_collection.create_index("last_updated")
        
        # Batch analytics collection
        batch_analytics_collection = self.db.batch_analytics
        
        await batch_analytics_collection.create_index("batch_id")
        await batch_analytics_collection.create_index("last_updated")
        
        logger.info("✅ Analytics indexes created")
    
    async def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about database indexes"""
        stats = {}
        
        collections = [
            "users", "assessments", "submissions", "batches", 
            "notifications", "coding_problems", "coding_solutions",
            "coding_sessions", "user_analytics", "assessment_analytics",
            "batch_analytics"
        ]
        
        for collection_name in collections:
            try:
                collection = self.db[collection_name]
                indexes = await collection.list_indexes().to_list(length=None)
                stats[collection_name] = {
                    "index_count": len(indexes),
                    "indexes": [index["name"] for index in indexes]
                }
            except Exception as e:
                logger.warning(f"Failed to get stats for {collection_name}: {e}")
                stats[collection_name] = {"error": str(e)}
        
        return stats
    
    async def analyze_query_performance(self, collection_name: str, query: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze query performance using explain"""
        try:
            collection = self.db[collection_name]
            explain_result = await collection.find(query).explain()
            
            return {
                "execution_time_ms": explain_result.get("executionTimeMillis", 0),
                "total_docs_examined": explain_result.get("totalDocsExamined", 0),
                "total_docs_returned": explain_result.get("totalDocsReturned", 0),
                "index_used": explain_result.get("indexUsed", None),
                "winning_plan": explain_result.get("winningPlan", {}),
                "rejected_plans": explain_result.get("rejectedPlans", [])
            }
        except Exception as e:
            logger.error(f"Failed to analyze query performance: {e}")
            return {"error": str(e)}
    
    async def drop_unused_indexes(self, collection_name: str, unused_threshold_days: int = 30):
        """Drop unused indexes (requires MongoDB 4.2+)"""
        try:
            collection = self.db[collection_name]
            
            # Get index usage stats
            stats = await self.db.command("collStats", collection_name, indexDetails=True)
            
            unused_indexes = []
            for index_name, index_stats in stats.get("indexSizes", {}).items():
                if index_name != "_id_":  # Don't drop the default _id index
                    # Check if index has been used recently
                    # This is a simplified check - in production, you'd want more sophisticated logic
                    if index_stats.get("accesses", {}).get("ops", 0) == 0:
                        unused_indexes.append(index_name)
            
            # Drop unused indexes
            for index_name in unused_indexes:
                try:
                    await collection.drop_index(index_name)
                    logger.info(f"Dropped unused index: {index_name}")
                except Exception as e:
                    logger.warning(f"Failed to drop index {index_name}: {e}")
            
            return {
                "dropped_indexes": unused_indexes,
                "count": len(unused_indexes)
            }
            
        except Exception as e:
            logger.error(f"Failed to drop unused indexes: {e}")
            return {"error": str(e)}
    
    async def optimize_collection(self, collection_name: str):
        """Optimize a collection by rebuilding indexes and compacting"""
        try:
            collection = self.db[collection_name]
            
            # Rebuild indexes
            await collection.reindex()
            
            # Compact collection (if supported)
            try:
                await self.db.command("compact", collection_name)
            except Exception as e:
                logger.warning(f"Collection compaction not supported: {e}")
            
            logger.info(f"Optimized collection: {collection_name}")
            return {"success": True, "collection": collection_name}
            
        except Exception as e:
            logger.error(f"Failed to optimize collection {collection_name}: {e}")
            return {"error": str(e)}

# Usage example
async def main():
    from motor.motor_asyncio import AsyncIOMotorClient
    
    # Initialize MongoDB client
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.edulearn
    
    # Create optimization service
    optimization_service = DatabaseOptimizationService(db)
    
    # Create all indexes
    await optimization_service.create_all_indexes()
    
    # Get index stats
    stats = await optimization_service.get_index_stats()
    print("Index Statistics:", stats)
    
    # Close client
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
