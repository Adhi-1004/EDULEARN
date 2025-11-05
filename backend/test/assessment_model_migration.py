"""
Assessment Model Unification Migration
Comprehensive migration to unify assessment models across the system
"""
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

class AssessmentModelMigration:
    """Handles migration to unified assessment model"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.assessments_collection = db.assessments
        self.teacher_assessments_collection = db.teacher_assessments
        self.migration_log = []
    
    async def migrate_to_unified_model(self) -> Dict[str, Any]:
        """Migrate all assessments to unified model"""
        logger.info("Starting assessment model unification migration")
        
        # Step 1: Create backup of existing data
        backup_result = await self._create_backup()
        
        # Step 2: Migrate regular assessments
        regular_migration = await self._migrate_regular_assessments()
        
        # Step 3: Migrate teacher assessments
        teacher_migration = await self._migrate_teacher_assessments()
        
        # Step 4: Update indexes
        index_result = await self._update_indexes()
        
        # Step 5: Validate migration
        validation_result = await self._validate_migration()
        
        result = {
            "backup": backup_result,
            "regular_assessments": regular_migration,
            "teacher_assessments": teacher_migration,
            "indexes": index_result,
            "validation": validation_result,
            "migration_log": self.migration_log
        }
        
        logger.info("Assessment model unification migration completed")
        return result
    
    async def rollback_migration(self) -> Dict[str, Any]:
        """Rollback the migration"""
        logger.info("Starting migration rollback")
        
        # Step 1: Restore from backup
        restore_result = await self._restore_from_backup()
        
        # Step 2: Recreate original indexes
        index_result = await self._restore_indexes()
        
        result = {
            "restore": restore_result,
            "indexes": index_result,
            "rollback_log": self.migration_log
        }
        
        logger.info("Migration rollback completed")
        return result
    
    async def _create_backup(self) -> Dict[str, Any]:
        """Create backup of existing data"""
        logger.info("Creating backup of existing assessment data")
        
        # Backup regular assessments
        regular_assessments = await self.assessments_collection.find({}).to_list(length=None)
        
        # Backup teacher assessments
        teacher_assessments = await self.teacher_assessments_collection.find({}).to_list(length=None)
        
        # Create backup collection
        backup_data = {
            "regular_assessments": regular_assessments,
            "teacher_assessments": teacher_assessments,
            "backup_timestamp": datetime.utcnow(),
            "migration_version": "1.0.0"
        }
        
        await self.db.assessment_backup.insert_one(backup_data)
        
        self.migration_log.append(f"Backup created: {len(regular_assessments)} regular, {len(teacher_assessments)} teacher assessments")
        
        return {
            "regular_count": len(regular_assessments),
            "teacher_count": len(teacher_assessments),
            "backup_id": str(backup_data["_id"])
        }
    
    async def _migrate_regular_assessments(self) -> Dict[str, Any]:
        """Migrate regular assessments to unified model"""
        logger.info("Migrating regular assessments")
        
        cursor = self.assessments_collection.find({})
        migrated_count = 0
        error_count = 0
        
        async for assessment in cursor:
            try:
                # Transform to unified model
                unified_assessment = await self._transform_regular_assessment(assessment)
                
                # Update the document
                await self.assessments_collection.update_one(
                    {"_id": assessment["_id"]},
                    {"$set": unified_assessment}
                )
                
                migrated_count += 1
                
            except Exception as e:
                logger.error(f"Error migrating assessment {assessment['_id']}: {str(e)}")
                error_count += 1
        
        self.migration_log.append(f"Migrated {migrated_count} regular assessments, {error_count} errors")
        
        return {
            "migrated": migrated_count,
            "errors": error_count
        }
    
    async def _migrate_teacher_assessments(self) -> Dict[str, Any]:
        """Migrate teacher assessments to unified model"""
        logger.info("Migrating teacher assessments")
        
        cursor = self.teacher_assessments_collection.find({})
        migrated_count = 0
        error_count = 0
        
        async for assessment in cursor:
            try:
                # Transform to unified model
                unified_assessment = await self._transform_teacher_assessment(assessment)
                
                # Insert into main assessments collection
                await self.assessments_collection.insert_one(unified_assessment)
                
                migrated_count += 1
                
            except Exception as e:
                logger.error(f"Error migrating teacher assessment {assessment['_id']}: {str(e)}")
                error_count += 1
        
        self.migration_log.append(f"Migrated {migrated_count} teacher assessments, {error_count} errors")
        
        return {
            "migrated": migrated_count,
            "errors": error_count
        }
    
    async def _transform_regular_assessment(self, assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Transform regular assessment to unified model"""
        return {
            # Core fields
            "title": assessment.get("title", ""),
            "description": assessment.get("description", ""),
            "subject": assessment.get("subject", ""),
            "difficulty": assessment.get("difficulty", "beginner"),
            "time_limit": assessment.get("time_limit", 60),
            "questions": assessment.get("questions", []),
            "total_questions": len(assessment.get("questions", [])),
            
            # Metadata
            "created_by": assessment.get("created_by", ""),
            "created_at": assessment.get("created_at", datetime.utcnow()),
            "updated_at": datetime.utcnow(),
            "is_active": assessment.get("is_active", True),
            
            # Assessment type
            "type": assessment.get("type", "mcq"),
            "max_attempts": assessment.get("max_attempts", 1),
            
            # Batch assignment
            "batches": assessment.get("batches", []),
            "assigned_students": assessment.get("assigned_students", []),
            
            # Status
            "status": assessment.get("status", "draft"),
            "published_at": assessment.get("published_at"),
            "due_date": assessment.get("due_date"),
            
            # Analytics
            "total_attempts": assessment.get("total_attempts", 0),
            "average_score": assessment.get("average_score", 0),
            "completion_rate": assessment.get("completion_rate", 0),
            
            # Settings
            "settings": {
                "randomize_questions": assessment.get("randomize_questions", False),
                "show_correct_answers": assessment.get("show_correct_answers", True),
                "allow_review": assessment.get("allow_review", True),
                "time_limit_enforced": assessment.get("time_limit_enforced", True)
            },
            
            # Migration metadata
            "migration_source": "regular_assessment",
            "original_id": str(assessment["_id"])
        }
    
    async def _transform_teacher_assessment(self, assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Transform teacher assessment to unified model"""
        return {
            # Core fields
            "title": assessment.get("title", ""),
            "description": assessment.get("description", ""),
            "subject": assessment.get("subject", ""),
            "difficulty": assessment.get("difficulty", "beginner"),
            "time_limit": assessment.get("time_limit", 60),
            "questions": assessment.get("questions", []),
            "total_questions": len(assessment.get("questions", [])),
            
            # Metadata
            "created_by": assessment.get("teacher_id", ""),
            "created_at": assessment.get("created_at", datetime.utcnow()),
            "updated_at": datetime.utcnow(),
            "is_active": assessment.get("is_active", True),
            
            # Assessment type
            "type": assessment.get("type", "ai_generated"),
            "max_attempts": assessment.get("max_attempts", 1),
            
            # Batch assignment
            "batches": assessment.get("batches", []),
            "assigned_students": assessment.get("assigned_students", []),
            
            # Status
            "status": assessment.get("status", "draft"),
            "published_at": assessment.get("published_at"),
            "due_date": assessment.get("due_date"),
            
            # Analytics
            "total_attempts": assessment.get("total_attempts", 0),
            "average_score": assessment.get("average_score", 0),
            "completion_rate": assessment.get("completion_rate", 0),
            
            # Settings
            "settings": {
                "randomize_questions": assessment.get("randomize_questions", False),
                "show_correct_answers": assessment.get("show_correct_answers", True),
                "allow_review": assessment.get("allow_review", True),
                "time_limit_enforced": assessment.get("time_limit_enforced", True)
            },
            
            # Migration metadata
            "migration_source": "teacher_assessment",
            "original_id": str(assessment["_id"])
        }
    
    async def _update_indexes(self) -> Dict[str, Any]:
        """Update indexes for unified model"""
        logger.info("Updating indexes for unified model")
        
        indexes_created = []
        
        # Create new indexes
        new_indexes = [
            {
                "keys": [("created_by", 1), ("created_at", -1)],
                "options": {"name": "creator_timestamp_idx"}
            },
            {
                "keys": [("type", 1), ("status", 1)],
                "options": {"name": "type_status_idx"}
            },
            {
                "keys": [("batches", 1), ("status", 1)],
                "options": {"name": "batch_status_idx"}
            },
            {
                "keys": [("subject", 1), ("difficulty", 1)],
                "options": {"name": "subject_difficulty_idx"}
            },
            {
                "keys": [("published_at", -1)],
                "options": {"name": "published_timestamp_idx"}
            }
        ]
        
        for index in new_indexes:
            try:
                await self.assessments_collection.create_index(
                    index["keys"],
                    **index["options"]
                )
                indexes_created.append(index["options"]["name"])
            except Exception as e:
                logger.error(f"Error creating index {index['options']['name']}: {str(e)}")
        
        self.migration_log.append(f"Created {len(indexes_created)} indexes")
        
        return {
            "indexes_created": indexes_created
        }
    
    async def _validate_migration(self) -> Dict[str, Any]:
        """Validate the migration"""
        logger.info("Validating migration")
        
        # Check total count
        total_count = await self.assessments_collection.count_documents({})
        
        # Check unified model compliance
        unified_count = await self.assessments_collection.count_documents({
            "migration_source": {"$exists": True}
        })
        
        # Check for missing required fields
        missing_fields = await self.assessments_collection.count_documents({
            "$or": [
                {"title": {"$exists": False}},
                {"created_by": {"$exists": False}},
                {"type": {"$exists": False}}
            ]
        })
        
        validation_result = {
            "total_assessments": total_count,
            "unified_assessments": unified_count,
            "missing_fields": missing_fields,
            "is_valid": missing_fields == 0
        }
        
        self.migration_log.append(f"Validation: {total_count} total, {unified_count} unified, {missing_fields} missing fields")
        
        return validation_result
    
    async def _restore_from_backup(self) -> Dict[str, Any]:
        """Restore from backup"""
        logger.info("Restoring from backup")
        
        # Find latest backup
        backup = await self.db.assessment_backup.find_one(
            {},
            sort=[("backup_timestamp", -1)]
        )
        
        if not backup:
            raise Exception("No backup found")
        
        # Clear existing collections
        await self.assessments_collection.drop()
        await self.teacher_assessments_collection.drop()
        
        # Restore data
        if backup["regular_assessments"]:
            await self.assessments_collection.insert_many(backup["regular_assessments"])
        
        if backup["teacher_assessments"]:
            await self.teacher_assessments_collection.insert_many(backup["teacher_assessments"])
        
        self.migration_log.append("Restored from backup")
        
        return {
            "restored_regular": len(backup["regular_assessments"]),
            "restored_teacher": len(backup["teacher_assessments"]),
            "backup_timestamp": backup["backup_timestamp"]
        }
    
    async def _restore_indexes(self) -> Dict[str, Any]:
        """Restore original indexes"""
        logger.info("Restoring original indexes")
        
        # Drop new indexes
        indexes_to_drop = [
            "creator_timestamp_idx",
            "type_status_idx",
            "batch_status_idx",
            "subject_difficulty_idx",
            "published_timestamp_idx"
        ]
        
        dropped_indexes = []
        for index_name in indexes_to_drop:
            try:
                await self.assessments_collection.drop_index(index_name)
                dropped_indexes.append(index_name)
            except Exception as e:
                logger.error(f"Error dropping index {index_name}: {str(e)}")
        
        self.migration_log.append(f"Dropped {len(dropped_indexes)} indexes")
        
        return {
            "dropped_indexes": dropped_indexes
        }

async def main():
    """Main migration function"""
    from app.core.config import settings
    from motor.motor_asyncio import AsyncIOMotorClient
    
    # Connect to database
    client = AsyncIOMotorClient(settings.mongo_uri)
    db = client[settings.db_name]
    
    # Initialize migration
    migration = AssessmentModelMigration(db)
    
    # Run migration
    result = await migration.migrate_to_unified_model()
    
    print("Migration completed:")
    print(json.dumps(result, indent=2, default=str))
    
    # Close connection
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
