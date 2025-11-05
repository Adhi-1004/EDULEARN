"""
Migration CLI Tool
Command-line interface for managing database migrations
"""
import asyncio
import argparse
import json
import sys
from datetime import datetime
from typing import Dict, List, Any
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from migration_manager import MigrationManager
from assessment_model_migration import AssessmentModelMigration

class MigrationCLI:
    """Command-line interface for migrations"""
    
    def __init__(self):
        self.client = None
        self.db = None
    
    async def connect(self):
        """Connect to database"""
        self.client = AsyncIOMotorClient(settings.mongo_uri)
        self.db = self.client[settings.db_name]
    
    async def disconnect(self):
        """Disconnect from database"""
        if self.client:
            self.client.close()
    
    async def status(self):
        """Show migration status"""
        await self.connect()
        
        migration_manager = MigrationManager(self.db)
        await migration_manager.initialize()
        
        status = await migration_manager.get_migration_status()
        
        print("Migration Status:")
        print(f"  Total migrations: {status['total']}")
        print(f"  Applied: {status['applied']}")
        print(f"  Pending: {status['pending']}")
        print(f"  Rolled back: {status['rolled_back']}")
        
        if status['migrations']:
            print("\nMigration History:")
            for migration in status['migrations']:
                status_icon = "✓" if migration['status'] == 'applied' else "✗" if migration['status'] == 'rolled_back' else "○"
                print(f"  {status_icon} {migration['name']} - {migration['status']}")
        
        await self.disconnect()
    
    async def apply(self, migration_id: str = None):
        """Apply migrations"""
        await self.connect()
        
        migration_manager = MigrationManager(self.db)
        await migration_manager.initialize()
        
        if migration_id:
            success = await migration_manager.apply_migration(migration_id)
            if success:
                print(f"✓ Applied migration: {migration_id}")
            else:
                print(f"✗ Failed to apply migration: {migration_id}")
                sys.exit(1)
        else:
            applied = await migration_manager.apply_all_pending()
            if applied:
                print(f"✓ Applied {len(applied)} migrations:")
                for mid in applied:
                    print(f"  - {mid}")
            else:
                print("No pending migrations to apply")
        
        await self.disconnect()
    
    async def rollback(self, migration_id: str = None):
        """Rollback migrations"""
        await self.connect()
        
        migration_manager = MigrationManager(self.db)
        await migration_manager.initialize()
        
        if migration_id:
            success = await migration_manager.rollback_migration(migration_id)
            if success:
                print(f"✓ Rolled back migration: {migration_id}")
            else:
                print(f"✗ Failed to rollback migration: {migration_id}")
                sys.exit(1)
        else:
            rolled_back = await migration_manager.rollback_all()
            if rolled_back:
                print(f"✓ Rolled back {len(rolled_back)} migrations:")
                for mid in rolled_back:
                    print(f"  - {mid}")
            else:
                print("No applied migrations to rollback")
        
        await self.disconnect()
    
    async def create(self, name: str, description: str = ""):
        """Create a new migration"""
        await self.connect()
        
        migration_manager = MigrationManager(self.db)
        await migration_manager.initialize()
        
        # Create migration template
        up_script = json.dumps({
            "operations": [
                {
                    "type": "create_collection",
                    "collection": "example_collection",
                    "options": {}
                }
            ]
        })
        
        down_script = json.dumps({
            "operations": [
                {
                    "type": "drop_collection",
                    "collection": "example_collection"
                }
            ]
        })
        
        migration_id = await migration_manager.create_migration(
            name=name,
            up_script=up_script,
            down_script=down_script,
            description=description
        )
        
        print(f"✓ Created migration: {migration_id}")
        print(f"  Name: {name}")
        print(f"  Description: {description}")
        
        await self.disconnect()
    
    async def assessment_migration(self):
        """Run assessment model migration"""
        await self.connect()
        
        migration = AssessmentModelMigration(self.db)
        
        print("Starting assessment model migration...")
        result = await migration.migrate_to_unified_model()
        
        print("✓ Assessment migration completed:")
        print(f"  Regular assessments: {result['regular_assessments']['migrated']}")
        print(f"  Teacher assessments: {result['teacher_assessments']['migrated']}")
        print(f"  Indexes created: {len(result['indexes']['indexes_created'])}")
        print(f"  Validation: {'✓' if result['validation']['is_valid'] else '✗'}")
        
        await self.disconnect()
    
    async def assessment_rollback(self):
        """Rollback assessment model migration"""
        await self.connect()
        
        migration = AssessmentModelMigration(self.db)
        
        print("Starting assessment migration rollback...")
        result = await migration.rollback_migration()
        
        print("✓ Assessment rollback completed:")
        print(f"  Restored regular: {result['restore']['restored_regular']}")
        print(f"  Restored teacher: {result['restore']['restored_teacher']}")
        print(f"  Indexes dropped: {len(result['indexes']['dropped_indexes'])}")
        
        await self.disconnect()
    
    async def backup(self):
        """Create database backup"""
        await self.connect()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"edulearn_backup_{timestamp}"
        
        # Create backup collection
        backup_data = {
            "backup_name": backup_name,
            "timestamp": datetime.utcnow(),
            "collections": {}
        }
        
        # Backup all collections
        collections = await self.db.list_collection_names()
        for collection_name in collections:
            if collection_name.startswith('system.'):
                continue
            
            collection = self.db[collection_name]
            documents = await collection.find({}).to_list(length=None)
            backup_data["collections"][collection_name] = documents
        
        await self.db.backups.insert_one(backup_data)
        
        print(f"✓ Database backup created: {backup_name}")
        print(f"  Collections backed up: {len(backup_data['collections'])}")
        
        await self.disconnect()
    
    async def restore(self, backup_name: str):
        """Restore database from backup"""
        await self.connect()
        
        # Find backup
        backup = await self.db.backups.find_one({"backup_name": backup_name})
        if not backup:
            print(f"✗ Backup not found: {backup_name}")
            sys.exit(1)
        
        # Restore collections
        restored_count = 0
        for collection_name, documents in backup["collections"].items():
            collection = self.db[collection_name]
            
            # Clear existing data
            await collection.drop()
            
            # Restore data
            if documents:
                await collection.insert_many(documents)
                restored_count += len(documents)
        
        print(f"✓ Database restored from backup: {backup_name}")
        print(f"  Documents restored: {restored_count}")
        
        await self.disconnect()

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description="EDULEARN Migration CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Status command
    subparsers.add_parser("status", help="Show migration status")
    
    # Apply command
    apply_parser = subparsers.add_parser("apply", help="Apply migrations")
    apply_parser.add_argument("migration_id", nargs="?", help="Specific migration ID to apply")
    
    # Rollback command
    rollback_parser = subparsers.add_parser("rollback", help="Rollback migrations")
    rollback_parser.add_argument("migration_id", nargs="?", help="Specific migration ID to rollback")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create new migration")
    create_parser.add_argument("name", help="Migration name")
    create_parser.add_argument("--description", help="Migration description")
    
    # Assessment migration commands
    subparsers.add_parser("assessment-migrate", help="Run assessment model migration")
    subparsers.add_parser("assessment-rollback", help="Rollback assessment model migration")
    
    # Backup commands
    subparsers.add_parser("backup", help="Create database backup")
    restore_parser = subparsers.add_parser("restore", help="Restore database from backup")
    restore_parser.add_argument("backup_name", help="Backup name to restore")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Create CLI instance
    cli = MigrationCLI()
    
    # Run command
    try:
        if args.command == "status":
            asyncio.run(cli.status())
        elif args.command == "apply":
            asyncio.run(cli.apply(args.migration_id))
        elif args.command == "rollback":
            asyncio.run(cli.rollback(args.migration_id))
        elif args.command == "create":
            asyncio.run(cli.create(args.name, args.description or ""))
        elif args.command == "assessment-migrate":
            asyncio.run(cli.assessment_migration())
        elif args.command == "assessment-rollback":
            asyncio.run(cli.assessment_rollback())
        elif args.command == "backup":
            asyncio.run(cli.backup())
        elif args.command == "restore":
            asyncio.run(cli.restore(args.backup_name))
        else:
            print(f"Unknown command: {args.command}")
            sys.exit(1)
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
