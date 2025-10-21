"""
Database Migration Manager
Comprehensive migration system with rollback capabilities
"""
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

class MigrationManager:
    """Manages database migrations with rollback support"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.migrations_collection = db.migrations
        self.migration_history = []
    
    async def initialize(self):
        """Initialize migration system"""
        # Create migrations collection if it doesn't exist
        collections = await self.db.list_collection_names()
        if 'migrations' not in collections:
            await self.db.create_collection('migrations')
            logger.info("Created migrations collection")
        
        # Load migration history
        cursor = self.migrations_collection.find().sort('applied_at', 1)
        self.migration_history = await cursor.to_list(length=None)
        logger.info(f"Loaded {len(self.migration_history)} migration records")
    
    async def create_migration(self, name: str, up_script: str, down_script: str, description: str = "") -> str:
        """Create a new migration"""
        migration_id = f"migration_{int(datetime.now().timestamp())}"
        
        migration_doc = {
            "_id": migration_id,
            "name": name,
            "description": description,
            "up_script": up_script,
            "down_script": down_script,
            "created_at": datetime.utcnow(),
            "applied_at": None,
            "rolled_back_at": None,
            "status": "pending"
        }
        
        await self.migrations_collection.insert_one(migration_doc)
        logger.info(f"Created migration: {migration_id}")
        return migration_id
    
    async def apply_migration(self, migration_id: str) -> bool:
        """Apply a specific migration"""
        migration = await self.migrations_collection.find_one({"_id": migration_id})
        if not migration:
            logger.error(f"Migration {migration_id} not found")
            return False
        
        if migration['status'] == 'applied':
            logger.warning(f"Migration {migration_id} already applied")
            return True
        
        try:
            # Execute up script
            await self._execute_script(migration['up_script'])
            
            # Update migration status
            await self.migrations_collection.update_one(
                {"_id": migration_id},
                {
                    "$set": {
                        "status": "applied",
                        "applied_at": datetime.utcnow()
                    }
                }
            )
            
            logger.info(f"Applied migration: {migration_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply migration {migration_id}: {str(e)}")
            return False
    
    async def rollback_migration(self, migration_id: str) -> bool:
        """Rollback a specific migration"""
        migration = await self.migrations_collection.find_one({"_id": migration_id})
        if not migration:
            logger.error(f"Migration {migration_id} not found")
            return False
        
        if migration['status'] != 'applied':
            logger.warning(f"Migration {migration_id} not applied, cannot rollback")
            return False
        
        try:
            # Execute down script
            await self._execute_script(migration['down_script'])
            
            # Update migration status
            await self.migrations_collection.update_one(
                {"_id": migration_id},
                {
                    "$set": {
                        "status": "rolled_back",
                        "rolled_back_at": datetime.utcnow()
                    }
                }
            )
            
            logger.info(f"Rolled back migration: {migration_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rollback migration {migration_id}: {str(e)}")
            return False
    
    async def apply_all_pending(self) -> List[str]:
        """Apply all pending migrations"""
        pending_migrations = await self.migrations_collection.find(
            {"status": "pending"}
        ).sort('created_at', 1).to_list(length=None)
        
        applied = []
        for migration in pending_migrations:
            success = await self.apply_migration(migration['_id'])
            if success:
                applied.append(migration['_id'])
            else:
                logger.error(f"Stopping migration process due to failure in {migration['_id']}")
                break
        
        return applied
    
    async def rollback_all(self) -> List[str]:
        """Rollback all applied migrations"""
        applied_migrations = await self.migrations_collection.find(
            {"status": "applied"}
        ).sort('applied_at', -1).to_list(length=None)
        
        rolled_back = []
        for migration in applied_migrations:
            success = await self.rollback_migration(migration['_id'])
            if success:
                rolled_back.append(migration['_id'])
            else:
                logger.error(f"Stopping rollback process due to failure in {migration['_id']}")
                break
        
        return rolled_back
    
    async def get_migration_status(self) -> Dict[str, Any]:
        """Get current migration status"""
        total = await self.migrations_collection.count_documents({})
        applied = await self.migrations_collection.count_documents({"status": "applied"})
        pending = await self.migrations_collection.count_documents({"status": "pending"})
        rolled_back = await self.migrations_collection.count_documents({"status": "rolled_back"})
        
        return {
            "total": total,
            "applied": applied,
            "pending": pending,
            "rolled_back": rolled_back,
            "migrations": self.migration_history
        }
    
    async def _execute_script(self, script: str):
        """Execute a migration script"""
        # This is a simplified version - in production, you'd want more sophisticated script execution
        try:
            # Parse and execute the script
            script_data = json.loads(script)
            
            for operation in script_data.get('operations', []):
                await self._execute_operation(operation)
                
        except json.JSONDecodeError:
            # If it's not JSON, treat as Python code
            exec(script)
    
    async def _execute_operation(self, operation: Dict[str, Any]):
        """Execute a single migration operation"""
        op_type = operation.get('type')
        
        if op_type == 'create_collection':
            await self._create_collection(operation)
        elif op_type == 'drop_collection':
            await self._drop_collection(operation)
        elif op_type == 'create_index':
            await self._create_index(operation)
        elif op_type == 'drop_index':
            await self._drop_index(operation)
        elif op_type == 'update_documents':
            await self._update_documents(operation)
        elif op_type == 'insert_documents':
            await self._insert_documents(operation)
        elif op_type == 'delete_documents':
            await self._delete_documents(operation)
        else:
            raise ValueError(f"Unknown operation type: {op_type}")
    
    async def _create_collection(self, operation: Dict[str, Any]):
        """Create a collection"""
        collection_name = operation['collection']
        options = operation.get('options', {})
        await self.db.create_collection(collection_name, **options)
        logger.info(f"Created collection: {collection_name}")
    
    async def _drop_collection(self, operation: Dict[str, Any]):
        """Drop a collection"""
        collection_name = operation['collection']
        await self.db.drop_collection(collection_name)
        logger.info(f"Dropped collection: {collection_name}")
    
    async def _create_index(self, operation: Dict[str, Any]):
        """Create an index"""
        collection_name = operation['collection']
        index_spec = operation['index']
        options = operation.get('options', {})
        
        collection = self.db[collection_name]
        await collection.create_index(index_spec, **options)
        logger.info(f"Created index on {collection_name}: {index_spec}")
    
    async def _drop_index(self, operation: Dict[str, Any]):
        """Drop an index"""
        collection_name = operation['collection']
        index_name = operation['index']
        
        collection = self.db[collection_name]
        await collection.drop_index(index_name)
        logger.info(f"Dropped index on {collection_name}: {index_name}")
    
    async def _update_documents(self, operation: Dict[str, Any]):
        """Update documents"""
        collection_name = operation['collection']
        filter_spec = operation['filter']
        update_spec = operation['update']
        options = operation.get('options', {})
        
        collection = self.db[collection_name]
        result = await collection.update_many(filter_spec, update_spec, **options)
        logger.info(f"Updated {result.modified_count} documents in {collection_name}")
    
    async def _insert_documents(self, operation: Dict[str, Any]):
        """Insert documents"""
        collection_name = operation['collection']
        documents = operation['documents']
        
        collection = self.db[collection_name]
        result = await collection.insert_many(documents)
        logger.info(f"Inserted {len(result.inserted_ids)} documents into {collection_name}")
    
    async def _delete_documents(self, operation: Dict[str, Any]):
        """Delete documents"""
        collection_name = operation['collection']
        filter_spec = operation['filter']
        
        collection = self.db[collection_name]
        result = await collection.delete_many(filter_spec)
        logger.info(f"Deleted {result.deleted_count} documents from {collection_name}")

# Migration scripts
MIGRATION_SCRIPTS = {
    "001_create_audit_logs": {
        "up": json.dumps({
            "operations": [
                {
                    "type": "create_collection",
                    "collection": "audit_logs",
                    "options": {
                        "validator": {
                            "$jsonSchema": {
                                "bsonType": "object",
                                "required": ["action", "user_id", "timestamp"],
                                "properties": {
                                    "action": {"bsonType": "string"},
                                    "user_id": {"bsonType": "string"},
                                    "timestamp": {"bsonType": "date"},
                                    "details": {"bsonType": "object"}
                                }
                            }
                        }
                    }
                },
                {
                    "type": "create_index",
                    "collection": "audit_logs",
                    "index": [("user_id", 1), ("timestamp", -1)],
                    "options": {"name": "user_timestamp_idx"}
                }
            ]
        }),
        "down": json.dumps({
            "operations": [
                {
                    "type": "drop_collection",
                    "collection": "audit_logs"
                }
            ]
        })
    },
    
    "002_create_performance_metrics": {
        "up": json.dumps({
            "operations": [
                {
                    "type": "create_collection",
                    "collection": "performance_metrics",
                    "options": {
                        "validator": {
                            "$jsonSchema": {
                                "bsonType": "object",
                                "required": ["metric_name", "value", "timestamp"],
                                "properties": {
                                    "metric_name": {"bsonType": "string"},
                                    "value": {"bsonType": "number"},
                                    "timestamp": {"bsonType": "date"},
                                    "tags": {"bsonType": "object"}
                                }
                            }
                        }
                    }
                },
                {
                    "type": "create_index",
                    "collection": "performance_metrics",
                    "index": [("metric_name", 1), ("timestamp", -1)],
                    "options": {"name": "metric_timestamp_idx"}
                }
            ]
        }),
        "down": json.dumps({
            "operations": [
                {
                    "type": "drop_collection",
                    "collection": "performance_metrics"
                }
            ]
        })
    },
    
    "003_add_user_analytics": {
        "up": json.dumps({
            "operations": [
                {
                    "type": "create_collection",
                    "collection": "user_analytics",
                    "options": {
                        "validator": {
                            "$jsonSchema": {
                                "bsonType": "object",
                                "required": ["user_id", "event_type", "timestamp"],
                                "properties": {
                                    "user_id": {"bsonType": "string"},
                                    "event_type": {"bsonType": "string"},
                                    "timestamp": {"bsonType": "date"},
                                    "properties": {"bsonType": "object"}
                                }
                            }
                        }
                    }
                },
                {
                    "type": "create_index",
                    "collection": "user_analytics",
                    "index": [("user_id", 1), ("event_type", 1), ("timestamp", -1)],
                    "options": {"name": "user_event_timestamp_idx"}
                }
            ]
        }),
        "down": json.dumps({
            "operations": [
                {
                    "type": "drop_collection",
                    "collection": "user_analytics"
                }
            ]
        })
    }
}

async def main():
    """Main migration function"""
    from app.core.config import settings
    from motor.motor_asyncio import AsyncIOMotorClient
    
    # Connect to database
    client = AsyncIOMotorClient(settings.mongo_uri)
    db = client[settings.db_name]
    
    # Initialize migration manager
    migration_manager = MigrationManager(db)
    await migration_manager.initialize()
    
    # Create migrations
    for migration_id, scripts in MIGRATION_SCRIPTS.items():
        await migration_manager.create_migration(
            name=migration_id,
            up_script=scripts['up'],
            down_script=scripts['down'],
            description=f"Migration {migration_id}"
        )
    
    # Apply all pending migrations
    applied = await migration_manager.apply_all_pending()
    print(f"Applied migrations: {applied}")
    
    # Get status
    status = await migration_manager.get_migration_status()
    print(f"Migration status: {status}")
    
    # Close connection
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
