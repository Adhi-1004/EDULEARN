# EDULEARN Database Migration System

## Overview

The EDULEARN migration system provides comprehensive database migration capabilities with rollback support, backup/restore functionality, and automated validation.

## Features

- **Automated Migrations**: Apply database schema changes automatically
- **Rollback Support**: Undo migrations safely with rollback scripts
- **Backup/Restore**: Create and restore database backups
- **Validation**: Validate migrations before and after application
- **CLI Interface**: Easy-to-use command-line interface
- **Assessment Model Unification**: Specialized migration for assessment models

## Installation

```bash
# Install dependencies
pip install motor pymongo

# Set up environment variables
export MONGO_URI="mongodb://localhost:27017"
export DB_NAME="edulearn"
```

## Usage

### Basic Commands

```bash
# Show migration status
python migration_cli.py status

# Apply all pending migrations
python migration_cli.py apply

# Apply specific migration
python migration_cli.py apply migration_001

# Rollback all migrations
python migration_cli.py rollback

# Rollback specific migration
python migration_cli.py rollback migration_001

# Create new migration
python migration_cli.py create "add_user_preferences" --description "Add user preferences collection"
```

### Assessment Model Migration

```bash
# Run assessment model unification migration
python migration_cli.py assessment-migrate

# Rollback assessment model migration
python migration_cli.py assessment-rollback
```

### Backup and Restore

```bash
# Create database backup
python migration_cli.py backup

# Restore from backup
python migration_cli.py restore edulearn_backup_20241217_143022
```

## Migration Scripts

### Creating Migrations

Migrations are defined as JSON scripts with operations:

```json
{
  "operations": [
    {
      "type": "create_collection",
      "collection": "user_preferences",
      "options": {
        "validator": {
          "$jsonSchema": {
            "bsonType": "object",
            "required": ["user_id", "preferences"],
            "properties": {
              "user_id": {"bsonType": "string"},
              "preferences": {"bsonType": "object"}
            }
          }
        }
      }
    },
    {
      "type": "create_index",
      "collection": "user_preferences",
      "index": [("user_id", 1)],
      "options": {"name": "user_id_idx", "unique": true}
    }
  ]
}
```

### Supported Operations

- **create_collection**: Create a new collection
- **drop_collection**: Drop a collection
- **create_index**: Create an index
- **drop_index**: Drop an index
- **update_documents**: Update documents
- **insert_documents**: Insert documents
- **delete_documents**: Delete documents

### Migration Examples

#### 1. Add User Preferences Collection

**Up Script:**
```json
{
  "operations": [
    {
      "type": "create_collection",
      "collection": "user_preferences",
      "options": {
        "validator": {
          "$jsonSchema": {
            "bsonType": "object",
            "required": ["user_id", "preferences"],
            "properties": {
              "user_id": {"bsonType": "string"},
              "preferences": {"bsonType": "object"}
            }
          }
        }
      }
    },
    {
      "type": "create_index",
      "collection": "user_preferences",
      "index": [("user_id", 1)],
      "options": {"name": "user_id_idx", "unique": true}
    }
  ]
}
```

**Down Script:**
```json
{
  "operations": [
    {
      "type": "drop_collection",
      "collection": "user_preferences"
    }
  ]
}
```

#### 2. Add Performance Indexes

**Up Script:**
```json
{
  "operations": [
    {
      "type": "create_index",
      "collection": "assessments",
      "index": [("created_by", 1), ("created_at", -1)],
      "options": {"name": "creator_timestamp_idx"}
    },
    {
      "type": "create_index",
      "collection": "assessments",
      "index": [("type", 1), ("status", 1)],
      "options": {"name": "type_status_idx"}
    }
  ]
}
```

**Down Script:**
```json
{
  "operations": [
    {
      "type": "drop_index",
      "collection": "assessments",
      "index": "creator_timestamp_idx"
    },
    {
      "type": "drop_index",
      "collection": "assessments",
      "index": "type_status_idx"
    }
  ]
}
```

#### 3. Update Document Schema

**Up Script:**
```json
{
  "operations": [
    {
      "type": "update_documents",
      "collection": "users",
      "filter": {"role": {"$exists": false}},
      "update": {"$set": {"role": "student"}},
      "options": {"multi": true}
    }
  ]
}
```

**Down Script:**
```json
{
  "operations": [
    {
      "type": "update_documents",
      "collection": "users",
      "filter": {"role": "student"},
      "update": {"$unset": {"role": ""}},
      "options": {"multi": true}
    }
  ]
}
```

## Assessment Model Migration

The assessment model migration unifies different assessment types into a single, consistent model:

### What It Does

1. **Backs up existing data** before making changes
2. **Transforms regular assessments** to unified model
3. **Migrates teacher assessments** to main collection
4. **Creates performance indexes** for better query performance
5. **Validates the migration** to ensure data integrity

### Unified Model Structure

```json
{
  "title": "Assessment Title",
  "description": "Assessment Description",
  "subject": "Mathematics",
  "difficulty": "intermediate",
  "time_limit": 60,
  "questions": [...],
  "total_questions": 10,
  "created_by": "teacher_id",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "is_active": true,
  "type": "mcq",
  "max_attempts": 3,
  "batches": ["batch_1", "batch_2"],
  "assigned_students": ["student_1", "student_2"],
  "status": "published",
  "published_at": "2024-01-01T00:00:00Z",
  "due_date": "2024-01-15T00:00:00Z",
  "total_attempts": 0,
  "average_score": 0,
  "completion_rate": 0,
  "settings": {
    "randomize_questions": false,
    "show_correct_answers": true,
    "allow_review": true,
    "time_limit_enforced": true
  },
  "migration_source": "regular_assessment",
  "original_id": "original_assessment_id"
}
```

## Best Practices

### 1. Always Create Backups

```bash
# Create backup before migration
python migration_cli.py backup

# Run migration
python migration_cli.py apply

# If something goes wrong, restore
python migration_cli.py restore edulearn_backup_20241217_143022
```

### 2. Test Migrations

```bash
# Test on development database first
export DB_NAME="edulearn_dev"
python migration_cli.py apply

# Test rollback
python migration_cli.py rollback

# Apply to production
export DB_NAME="edulearn_production"
python migration_cli.py apply
```

### 3. Validate Migrations

```bash
# Check status before and after
python migration_cli.py status

# Run assessment migration validation
python migration_cli.py assessment-migrate
```

### 4. Use Descriptive Names

```bash
# Good
python migration_cli.py create "add_user_preferences"

# Bad
python migration_cli.py create "migration_001"
```

## Troubleshooting

### Common Issues

1. **Migration Fails**: Check logs and rollback if necessary
2. **Rollback Fails**: Restore from backup
3. **Index Creation Fails**: Check for existing indexes
4. **Validation Fails**: Review data integrity

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python migration_cli.py status
```

### Manual Recovery

```bash
# Connect to MongoDB directly
mongo edulearn

# Check migration status
db.migrations.find().pretty()

# Manual rollback
db.migrations.updateOne(
  {"_id": "migration_id"},
  {"$set": {"status": "rolled_back"}}
)
```

## Production Deployment

### 1. Pre-deployment Checklist

- [ ] Create backup
- [ ] Test migrations on staging
- [ ] Verify rollback procedures
- [ ] Check disk space
- [ ] Notify team of maintenance window

### 2. Deployment Steps

```bash
# 1. Create backup
python migration_cli.py backup

# 2. Apply migrations
python migration_cli.py apply

# 3. Verify status
python migration_cli.py status

# 4. Test application
curl http://localhost:8000/health
```

### 3. Rollback Plan

```bash
# If issues occur
python migration_cli.py rollback

# Or restore from backup
python migration_cli.py restore latest_backup_name
```

## Monitoring

### Migration Logs

```bash
# Check migration history
python migration_cli.py status

# View detailed logs
tail -f /var/log/edulearn/migrations.log
```

### Performance Impact

- Migrations run during maintenance windows
- Large collections may take time to migrate
- Index creation can impact performance temporarily
- Monitor disk space during migrations

## Security Considerations

- Migrations run with database admin privileges
- Backup files contain sensitive data
- Secure backup storage and access
- Audit migration activities
- Use encrypted connections

## Support

For migration support:
- Check logs for error messages
- Review migration scripts for syntax errors
- Test on development environment first
- Contact system administrator for complex issues

This migration system ensures safe, reliable database updates for the EDULEARN platform.
