"""
Database Migration Script
Converts single batch_id to multiple batch_ids array for students

Run this script once to migrate existing data:
    python -m backend.migrate_batch_to_batch_ids
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app.db import get_db, init_db
from bson import ObjectId


async def migrate_batch_ids():
    """Migrate batch_id (single) to batch_ids (array) for all users"""
    
    print("[MIGRATION] Starting batch_id to batch_ids migration...")
    print("[MIGRATION] Initializing database connection...")
    
    # Initialize database
    await init_db()
    db = await get_db()
    
    # Find all users with batch_id field
    print("[MIGRATION] Finding users with batch_id...")
    users_with_batch_id = await db.users.find(
        {"batch_id": {"$exists": True}}
    ).to_list(length=None)
    
    print(f"[MIGRATION] Found {len(users_with_batch_id)} users with batch_id")
    
    migrated_count = 0
    skipped_count = 0
    error_count = 0
    
    for user in users_with_batch_id:
        try:
            user_id = user["_id"]
            batch_id = user.get("batch_id")
            
            # Check if user already has batch_ids array
            if "batch_ids" in user:
                print(f"[SKIP] User {user.get('email', user_id)} already has batch_ids array")
                skipped_count += 1
                continue
            
            # Prepare the new batch_ids array
            batch_ids = []
            if batch_id:
                # Convert to string if it's ObjectId
                if isinstance(batch_id, ObjectId):
                    batch_ids = [str(batch_id)]
                else:
                    batch_ids = [batch_id]
            
            # Update the user document
            result = await db.users.update_one(
                {"_id": user_id},
                {
                    "$set": {"batch_ids": batch_ids},
                    "$unset": {"batch_id": ""}
                }
            )
            
            if result.modified_count > 0:
                migrated_count += 1
                print(f"[OK] Migrated user {user.get('email', user_id)}: batch_id -> batch_ids {batch_ids}")
            else:
                print(f"[WARN] No changes for user {user.get('email', user_id)}")
                
        except Exception as e:
            error_count += 1
            print(f"[ERROR] Failed to migrate user {user.get('email', user_id)}: {str(e)}")
    
    # Summary
    print("\n" + "=" * 60)
    print("[MIGRATION] Migration Summary:")
    print(f"  Total users found: {len(users_with_batch_id)}")
    print(f"  Successfully migrated: {migrated_count}")
    print(f"  Skipped (already migrated): {skipped_count}")
    print(f"  Errors: {error_count}")
    print("=" * 60)
    
    if error_count == 0:
        print("[SUCCESS] Migration completed successfully!")
    else:
        print(f"[WARNING] Migration completed with {error_count} errors")
    
    # Verify migration
    print("\n[VERIFICATION] Verifying migration...")
    users_with_old_field = await db.users.count_documents({"batch_id": {"$exists": True}})
    users_with_new_field = await db.users.count_documents({"batch_ids": {"$exists": True}})
    
    print(f"  Users with batch_id (should be 0): {users_with_old_field}")
    print(f"  Users with batch_ids: {users_with_new_field}")
    
    if users_with_old_field == 0:
        print("[SUCCESS] Verification passed - all users migrated")
    else:
        print(f"[WARNING] {users_with_old_field} users still have old batch_id field")
    
    return {
        "total": len(users_with_batch_id),
        "migrated": migrated_count,
        "skipped": skipped_count,
        "errors": error_count
    }


if __name__ == "__main__":
    print("=" * 60)
    print(" EDULEARN Database Migration: batch_id → batch_ids")
    print("=" * 60)
    print()
    
    result = asyncio.run(migrate_batch_ids())
    
    print()
    sys.exit(0 if result["errors"] == 0 else 1)

