# Project Structure Cleanup

## Changes Made

### 1. Eliminated Duplicate Files
- **Removed duplicate main.py files**: Consolidated into single entry point
- **Consolidated API files**: Combined related functionality into single files
- **Removed ambiguous naming**: Clear, descriptive file names

### 2. New File Structure

#### Entry Points
- `backend/start_server.py` - Main server startup script
- `backend/run.py` - Alternative entry point
- `backend/app/main.py` - FastAPI application (unchanged location)

#### Consolidated API Files
- `backend/app/api/admin_consolidated.py` - All admin functionality
- `backend/app/api/users_consolidated.py` - All user management
- `backend/app/api/teacher_consolidated.py` - All teacher dashboard features

#### Removed Files
- `backend/main.py` (duplicate)
- `backend/app/api/admin.py` (merged into admin_consolidated.py)
- `backend/app/api/admin_dashboard.py` (merged into admin_consolidated.py)
- `backend/app/api/enhanced_admin_dashboard.py` (merged into admin_consolidated.py)
- `backend/app/api/users.py` (merged into users_consolidated.py)
- `backend/app/api/enhanced_users.py` (merged into users_consolidated.py)
- `backend/app/api/teacher_dashboard.py` (merged into teacher_consolidated.py)
- `backend/app/api/enhanced_teacher_dashboard.py` (merged into teacher_consolidated.py)

## How to Run the Application

### Option 1: Using the startup script (Recommended)
```bash
cd backend
python start_server.py
```

### Option 2: Using uvicorn directly
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 5001 --reload
```

### Option 3: Using the run script
```bash
cd backend
python run.py
```

## Benefits of the Cleanup

1. **No More Import Confusion**: Single entry point eliminates relative import issues
2. **Clear API Structure**: Consolidated files with all related functionality
3. **Easier Maintenance**: No duplicate code to maintain
4. **Better Organization**: Logical grouping of related features
5. **Simplified Development**: Clear file structure for new developers

## API Endpoints

All endpoints are now organized under clear prefixes:
- `/auth/*` - Authentication
- `/api/users/*` - User management
- `/api/teacher/*` - Teacher dashboard
- `/api/admin/*` - Admin dashboard
- `/api/coding/*` - Coding platform
- `/api/assessments/*` - Assessments
