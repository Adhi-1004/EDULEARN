"""
Database Maintenance Script
Ongoing database optimization and maintenance tasks
"""
import asyncio
import logging
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from app.services.database_optimization_service import DatabaseOptimizationService
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseMaintenanceService:
    """Service for ongoing database maintenance and optimization"""
    
    def __init__(self, db):
        self.db = db
        self.optimization_service = DatabaseOptimizationService(db)
    
    async def run_maintenance_tasks(self):
        """Run all maintenance tasks"""
        logger.info("🔧 Starting database maintenance tasks...")
        
        try:
            # Analyze query performance
            await self.analyze_performance()
            
            # Clean up old data
            await self.cleanup_old_data()
            
            # Optimize collections
            await self.optimize_collections()
            
            # Update statistics
            await self.update_statistics()
            
            logger.info("✅ Database maintenance completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Database maintenance failed: {e}")
            raise
    
    async def analyze_performance(self):
        """Analyze database performance"""
        logger.info("📊 Analyzing database performance...")
        
        # Get index statistics
        stats = await self.optimization_service.get_index_stats()
        
        # Log performance metrics
        for collection, stat in stats.items():
            if "error" not in stat:
                logger.info(f"  {collection}: {stat['index_count']} indexes")
        
        # Test common queries
        common_queries = [
            ("users", {"role": "student", "is_active": True}),
            ("assessments", {"is_active": True, "status": "published"}),
            ("submissions", {"status": "submitted"}),
            ("batches", {"is_active": True})
        ]
        
        for collection, query in common_queries:
            try:
                result = await self.optimization_service.analyze_query_performance(collection, query)
                if "error" not in result:
                    logger.info(f"  {collection} query: {result['execution_time_ms']}ms")
            except Exception as e:
                logger.warning(f"  Failed to analyze {collection}: {e}")
    
    async def cleanup_old_data(self):
        """Clean up old and unnecessary data"""
        logger.info("🧹 Cleaning up old data...")
        
        # Clean up old sessions
        await self._cleanup_old_sessions()
        
        # Clean up old notifications
        await self._cleanup_old_notifications()
        
        # Clean up old analytics
        await self._cleanup_old_analytics()
    
    async def _cleanup_old_sessions(self):
        """Clean up old coding sessions"""
        try:
            sessions_collection = self.db.coding_sessions
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            
            result = await sessions_collection.delete_many({
                "last_activity": {"$lt": cutoff_date},
                "is_active": False
            })
            
            logger.info(f"  Cleaned up {result.deleted_count} old coding sessions")
            
        except Exception as e:
            logger.warning(f"  Failed to cleanup sessions: {e}")
    
    async def _cleanup_old_notifications(self):
        """Clean up old read notifications"""
        try:
            notifications_collection = self.db.notifications
            cutoff_date = datetime.utcnow() - timedelta(days=90)
            
            result = await notifications_collection.delete_many({
                "is_read": True,
                "read_at": {"$lt": cutoff_date}
            })
            
            logger.info(f"  Cleaned up {result.deleted_count} old notifications")
            
        except Exception as e:
            logger.warning(f"  Failed to cleanup notifications: {e}")
    
    async def _cleanup_old_analytics(self):
        """Clean up old analytics data"""
        try:
            analytics_collection = self.db.user_analytics
            cutoff_date = datetime.utcnow() - timedelta(days=365)
            
            result = await analytics_collection.delete_many({
                "last_updated": {"$lt": cutoff_date}
            })
            
            logger.info(f"  Cleaned up {result.deleted_count} old analytics records")
            
        except Exception as e:
            logger.warning(f"  Failed to cleanup analytics: {e}")
    
    async def optimize_collections(self):
        """Optimize database collections"""
        logger.info("⚡ Optimizing collections...")
        
        collections_to_optimize = [
            "users", "assessments", "submissions", "batches",
            "notifications", "coding_problems", "coding_solutions"
        ]
        
        for collection_name in collections_to_optimize:
            try:
                result = await self.optimization_service.optimize_collection(collection_name)
                if "error" not in result:
                    logger.info(f"  Optimized {collection_name}")
                else:
                    logger.warning(f"  Failed to optimize {collection_name}: {result['error']}")
            except Exception as e:
                logger.warning(f"  Failed to optimize {collection_name}: {e}")
    
    async def update_statistics(self):
        """Update database statistics"""
        logger.info("📈 Updating statistics...")
        
        try:
            # Update collection statistics
            collections = ["users", "assessments", "submissions", "batches", "notifications"]
            
            for collection_name in collections:
                try:
                    collection = self.db[collection_name]
                    count = await collection.count_documents({})
                    logger.info(f"  {collection_name}: {count} documents")
                except Exception as e:
                    logger.warning(f"  Failed to count {collection_name}: {e}")
            
        except Exception as e:
            logger.warning(f"  Failed to update statistics: {e}")

async def main():
    """Main function for database maintenance"""
    try:
        # Initialize MongoDB client
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = client[settings.DATABASE_NAME]
        
        # Create maintenance service
        maintenance_service = DatabaseMaintenanceService(db)
        
        # Run maintenance tasks
        await maintenance_service.run_maintenance_tasks()
        
        logger.info("🎉 Database maintenance completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Database maintenance failed: {e}")
        exit(1)
    finally:
        # Close client
        client.close()

if __name__ == "__main__":
    asyncio.run(main())
