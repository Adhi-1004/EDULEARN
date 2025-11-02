# Multi-Batch Student Mapping Migration Guide

## Overview
This migration enables students to be mapped to multiple batches simultaneously, allowing a single student to access assessments from different teachers/subjects.

## Changes Made

### 1. Database Schema Changes
- **Before**: Students had single `batch_id` field
- **After**: Students have array `batch_ids` field
- **Index Added**: Created index on `batch_ids` field for query performance

### 2. Migration Script
Created `backend/migrate_batch_to_batch_ids.py` to convert existing data:
- Converts `batch_id` (single value) → `batch_ids` (array)
- Preserves existing batch assignments
- Removes old `batch_id` field after migration

### 3. API Endpoints Updated

#### Student Assignment (`backend/app/api/teacher.py` & `backend/app/api/teacher_modules/students.py`)
- **Add Student to Batch**: Now uses `$addToSet` to add to array (prevents duplicates)
- **Remove Student from Batch**: Uses `$pull` to remove from array
- **Bulk Assignment**: Updated to use `$addToSet`

#### Assessment Access (`backend/app/api/assessments.py`)
- Access checks now verify if ANY of student's batches match assigned batches
- Updated queries to use `{"$in": student_batch_ids}`
- Modified upcoming assessments endpoint to support multi-batch

#### Get Students Queries
- **Get Batch Students**: Updated query to use `"batch_ids": batch_id`
- **Get Students by Teacher**: Updated to query array field
- **Response Formatting**: Now returns `batch_ids` array and `batch_names` array

### 4. Files Modified

1. **`backend/app/db/session.py`**
   - Added index: `db.users.create_index([("batch_ids", 1)])`

2. **`backend/app/api/teacher.py`**
   - Updated student creation to use `batch_ids` array
   - Updated add student to use `$addToSet`
   - Updated remove student to use `$pull`
   - Updated get students query
   - Updated batch info display to show multiple batches

3. **`backend/app/api/teacher_modules/students.py`**
   - Updated assignment endpoint to use `$addToSet`
   - Updated query filters for multi-batch
   - Updated response to include batch_ids and batch_names arrays

4. **`backend/app/api/teacher_modules/batches.py`**
   - Updated get batch students query to use array field

5. **`backend/app/api/assessments.py`**
   - Updated access checks to use batch_ids array
   - Updated upcoming assessments query
   - Updated student performance responses

## How to Run Migration

### Step 1: Backup Database
```bash
mongodump --uri="mongodb://127.0.0.1:27017/edulearn" --out=backup_before_batch_migration
```

### Step 2: Run Migration Script
```bash
cd backend
python -m migrate_batch_to_batch_ids
```

### Step 3: Verify Migration
The script will output:
- Number of users migrated
- Number of users skipped (already migrated)
- Any errors encountered
- Verification statistics

### Step 4: Restart Backend
The backend will auto-reload if using uvicorn with `--reload`, otherwise restart manually.

## Database Queries

### Before Migration
```javascript
// Old: Query students in a batch
db.users.find({ batch_id: "batch123" })

// Old: Check if student has access
student.batch_id === assessment.assigned_batches[0]
```

### After Migration
```javascript
// New: Query students in a batch (MongoDB array contains)
db.users.find({ batch_ids: "batch123" })

// New: Query students in multiple batches
db.users.find({ batch_ids: { $in: ["batch123", "batch456"] } })

// New: Check if student has access (ANY batch matches)
student.batch_ids.some(bid => assessment.assigned_batches.includes(bid))
```

## API Response Changes

### Before
```json
{
  "id": "student123",
  "name": "John Doe",
  "batch_id": "batch123",
  "batch_name": "Math Class A"
}
```

### After
```json
{
  "id": "student123",
  "name": "John Doe",
  "batch_ids": ["batch123", "batch456"],
  "batch_names": ["Math Class A", "Science Class B"],
  "batch_name": "Math Class A, Science Class B"
}
```

## Benefits

1. **Multi-Subject Learning**: Students can attend classes from multiple teachers
2. **Flexible Assignment**: Add students to new batches without removing from existing ones
3. **Cross-Subject Assessments**: Students see assessments from all their teachers
4. **Real-World Mapping**: Mimics actual school structure

## Backward Compatibility

- `batch_name` field still returned (comma-separated for multiple batches)
- Existing API endpoints continue to work
- Migration is non-destructive (creates new field before removing old one)

## Testing Checklist

- [ ] Run migration script successfully
- [ ] Verify all students have batch_ids array
- [ ] Test adding student to multiple batches
- [ ] Test removing student from one batch (should remain in others)
- [ ] Test assessment access for students in multiple batches
- [ ] Test teacher viewing students across batches
- [ ] Verify frontend displays multiple batches correctly

## Rollback (If Needed)

If you need to rollback:

```javascript
// Restore from backup
mongorestore --uri="mongodb://127.0.0.1:27017/edulearn" backup_before_batch_migration/edulearn

// Or manually revert (if batch_ids has single value)
db.users.find({ batch_ids: { $exists: true } }).forEach(user => {
  if (user.batch_ids && user.batch_ids.length > 0) {
    db.users.updateOne(
      { _id: user._id },
      {
        $set: { batch_id: user.batch_ids[0] },
        $unset: { batch_ids: "" }
      }
    );
  }
});
```

## Support

If you encounter issues:
1. Check migration script output for errors
2. Verify database indexes are created
3. Check backend logs for query errors
4. Ensure all files were updated correctly

---

**Migration completed**: All code changes implemented
**Ready to run**: Execute migration script when ready
**Status**: ✅ All TODOs completed

