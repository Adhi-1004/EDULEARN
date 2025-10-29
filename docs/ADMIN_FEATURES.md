# 👑 Admin Control Panel Features

## Table of Contents
1. [Overview](#overview)
2. [Platform Analytics](#platform-analytics)
3. [User Management](#user-management)
4. [System Health Monitoring](#system-health-monitoring)
5. [Bulk Operations](#bulk-operations)
6. [Content Oversight](#content-oversight)

---

## Overview

The Admin Control Panel provides comprehensive platform management, monitoring, and administrative capabilities.

### Key Capabilities
- 📊 Platform-wide analytics and statistics
- 👥 Complete user management (CRUD)
- 🏥 System health monitoring
- 📥 Bulk import/export operations
- 🔍 Content moderation and oversight
- 📈 Teacher performance analytics
- 💾 Database health checks

---

## Platform Analytics

### Comprehensive Statistics Dashboard

```python
# File: backend/app/api/admin.py
@router.get("/analytics/platform")
async def get_platform_analytics(
    current_user: dict = Depends(require_role("admin"))
):
    """Get comprehensive platform statistics"""
    db = await get_db()
    
    # User statistics
    total_users = await db.users.count_documents({})
    students = await db.users.count_documents({"role": "student"})
    teachers = await db.users.count_documents({"role": "teacher"})
    admins = await db.users.count_documents({"role": "admin"})
    
    # Activity statistics
    total_assessments = await db.assessments.count_documents({})
    total_submissions = await db.assessment_submissions.count_documents({})
    total_coding_problems = await db.coding_problems.count_documents({})
    total_coding_solutions = await db.coding_solutions.count_documents({})
    
    # Calculate average scores
    submissions = await db.assessment_submissions.find({}).to_list(length=None)
    avg_assessment_score = sum(s["percentage"] for s in submissions) / len(submissions) if submissions else 0
    
    # Recent activity (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    new_users_week = await db.users.count_documents({
        "created_at": {"$gte": week_ago}
    })
    submissions_week = await db.assessment_submissions.count_documents({
        "submitted_at": {"$gte": week_ago}
    })
    
    # Batch statistics
    total_batches = await db.batches.count_documents({"is_active": True})
    
    return {
        "users": {
            "total": total_users,
            "students": students,
            "teachers": teachers,
            "admins": admins,
            "new_this_week": new_users_week
        },
        "assessments": {
            "total_assessments": total_assessments,
            "total_submissions": total_submissions,
            "average_score": round(avg_assessment_score, 2),
            "submissions_this_week": submissions_week
        },
        "coding": {
            "total_problems": total_coding_problems,
            "total_solutions": total_coding_solutions
        },
        "batches": {
            "total_active": total_batches
        }
    }
```

### Time-Series Analytics

```python
@router.get("/analytics/time-series")
async def get_time_series_analytics(
    period: str = Query("month", regex="^(day|week|month)$"),
    current_user: dict = Depends(require_role("admin"))
):
    """Get time-series analytics data"""
    db = await get_db()
    
    # Define time periods
    periods = {
        "day": 1,
        "week": 7,
        "month": 30
    }
    days = periods[period]
    
    # Get data for each day
    time_series_data = []
    for i in range(days):
        date = datetime.utcnow() - timedelta(days=days - i - 1)
        next_date = date + timedelta(days=1)
        
        # Users registered
        users_registered = await db.users.count_documents({
            "created_at": {
                "$gte": date,
                "$lt": next_date
            }
        })
        
        # Assessments taken
        assessments_taken = await db.assessment_submissions.count_documents({
            "submitted_at": {
                "$gte": date,
                "$lt": next_date
            }
        })
        
        # Coding problems solved
        problems_solved = await db.coding_solutions.count_documents({
            "submitted_at": {
                "$gte": date,
                "$lt": next_date
            },
            "status": "accepted"
        })
        
        time_series_data.append({
            "date": date.strftime("%Y-%m-%d"),
            "users_registered": users_registered,
            "assessments_taken": assessments_taken,
            "problems_solved": problems_solved
        })
    
    return {
        "period": period,
        "data": time_series_data
    }
```

---

## User Management

### Complete CRUD Operations

```python
# File: backend/app/api/admin.py

@router.get("/users")
async def get_all_users(
    role: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(require_role("admin"))
):
    """Get all users with pagination and filtering"""
    db = await get_db()
    
    # Build query
    query = {}
    if role:
        query["role"] = role
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}}
        ]
    
    # Get users
    users = await db.users.find(query).skip(skip).limit(limit).to_list(length=limit)
    total = await db.users.count_documents(query)
    
    # Enrich with statistics
    for user in users:
        if user["role"] == "student":
            user["stats"] = await get_student_stats(db, user["_id"])
        elif user["role"] == "teacher":
            user["stats"] = await get_teacher_stats(db, user["_id"])
    
    return {
        "users": users,
        "total": total,
        "page": skip // limit + 1,
        "pages": (total + limit - 1) // limit
    }

@router.post("/users")
async def create_user(
    user_data: UserCreate,
    current_user: dict = Depends(require_role("admin"))
):
    """Create a new user"""
    db = await get_db()
    
    # Check if email exists
    existing = await db.users.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(400, "Email already exists")
    
    # Hash password
    hashed_pwd = pwd_context.hash(user_data.password)
    
    # Create user document
    user_doc = {
        "_id": str(uuid4()),
        "name": user_data.name,
        "email": user_data.email,
        "password": hashed_pwd,
        "role": user_data.role,
        "created_at": datetime.utcnow(),
        "is_active": True,
        "created_by": "admin"
    }
    
    await db.users.insert_one(user_doc)
    
    # Initialize stats
    if user_data.role == "student":
        await initialize_user_stats(db, user_doc["_id"])
    
    return {
        "message": "User created successfully",
        "user_id": user_doc["_id"]
    }

@router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    update_data: UserUpdate,
    current_user: dict = Depends(require_role("admin"))
):
    """Update user information"""
    db = await get_db()
    
    # Build update document
    update_dict = {}
    if update_data.name:
        update_dict["name"] = update_data.name
    if update_data.email:
        # Check email uniqueness
        existing = await db.users.find_one({
            "email": update_data.email,
            "_id": {"$ne": user_id}
        })
        if existing:
            raise HTTPException(400, "Email already in use")
        update_dict["email"] = update_data.email
    if update_data.role:
        update_dict["role"] = update_data.role
    if update_data.is_active is not None:
        update_dict["is_active"] = update_data.is_active
    
    if not update_dict:
        raise HTTPException(400, "No fields to update")
    
    result = await db.users.update_one(
        {"_id": user_id},
        {"$set": update_dict}
    )
    
    if result.modified_count == 0:
        raise HTTPException(404, "User not found")
    
    return {"message": "User updated successfully"}

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: dict = Depends(require_role("admin"))
):
    """Soft delete user (deactivate)"""
    db = await get_db()
    
    # Prevent self-deletion
    if user_id == current_user["_id"]:
        raise HTTPException(400, "Cannot delete your own account")
    
    # Soft delete (deactivate)
    result = await db.users.update_one(
        {"_id": user_id},
        {
            "$set": {
                "is_active": False,
                "deactivated_at": datetime.utcnow(),
                "deactivated_by": current_user["_id"]
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(404, "User not found")
    
    return {"message": "User deactivated successfully"}

@router.post("/users/{user_id}/reset-password")
async def reset_user_password(
    user_id: str,
    new_password: str,
    current_user: dict = Depends(require_role("admin"))
):
    """Reset a user's password"""
    db = await get_db()
    
    # Hash new password
    hashed_pwd = pwd_context.hash(new_password)
    
    # Update password
    result = await db.users.update_one(
        {"_id": user_id},
        {
            "$set": {
                "password": hashed_pwd,
                "password_reset_at": datetime.utcnow(),
                "password_reset_by": current_user["_id"]
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(404, "User not found")
    
    # Create notification
    await create_notification(
        db,
        user_id,
        "Password Reset",
        "Your password has been reset by an administrator.",
        "security"
    )
    
    return {"message": "Password reset successfully"}
```

---

## System Health Monitoring

### Comprehensive Health Checks

```python
# File: backend/app/api/health.py
@router.get("/comprehensive")
async def comprehensive_health_check():
    """Comprehensive system health check"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {}
    }
    
    # 1. API Health
    health_status["components"]["api"] = {
        "status": "healthy",
        "uptime": get_uptime()
    }
    
    # 2. Database Health
    try:
        db = await get_db()
        await db.command("ping")
        
        # Check collections
        collections = await db.list_collection_names()
        
        health_status["components"]["database"] = {
            "status": "healthy",
            "collections_count": len(collections),
            "collections": collections
        }
    except Exception as e:
        health_status["components"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "unhealthy"
    
    # 3. AI Services Health
    try:
        # Test Gemini AI
        gemini_service = GeminiCodingService()
        response = gemini_service.model.generate_content("Test")
        
        health_status["components"]["gemini_ai"] = {
            "status": "healthy",
            "response_time": "< 1s"
        }
    except Exception as e:
        health_status["components"]["gemini_ai"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # 4. Judge0 Service Health
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{JUDGE0_API_URL}/about") as response:
                if response.status == 200:
                    health_status["components"]["judge0"] = {
                        "status": "healthy"
                    }
                else:
                    raise Exception(f"Status code: {response.status}")
    except Exception as e:
        health_status["components"]["judge0"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # 5. System Resources
    import psutil
    
    health_status["components"]["system"] = {
        "status": "healthy",
        "cpu_usage": psutil.cpu_percent(),
        "memory_usage": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent
    }
    
    # Overall status
    unhealthy_components = [
        k for k, v in health_status["components"].items()
        if v["status"] == "unhealthy"
    ]
    
    if unhealthy_components:
        health_status["status"] = "degraded"
        health_status["unhealthy_components"] = unhealthy_components
    
    return health_status

@router.get("/metrics")
async def get_health_metrics():
    """Get detailed health metrics for monitoring systems"""
    db = await get_db()
    
    # Database metrics
    db_stats = await db.command("dbStats")
    
    # Collection sizes
    collection_stats = {}
    for collection_name in ["users", "assessments", "coding_problems"]:
        stats = await db.command("collStats", collection_name)
        collection_stats[collection_name] = {
            "count": stats["count"],
            "size": stats["size"],
            "avgObjSize": stats.get("avgObjSize", 0)
        }
    
    return {
        "database": {
            "dataSize": db_stats["dataSize"],
            "storageSize": db_stats["storageSize"],
            "collections": collection_stats
        },
        "system": {
            "cpu": psutil.cpu_percent(),
            "memory": psutil.virtual_memory().percent,
            "disk": psutil.disk_usage('/').percent
        }
    }
```

---

## Bulk Operations

### Bulk Import Users

```python
@router.post("/users/bulk-import")
async def bulk_import_users(
    file: UploadFile,
    current_user: dict = Depends(require_role("admin"))
):
    """Bulk import users from CSV file"""
    db = await get_db()
    
    # Read file
    contents = await file.read()
    
    # Parse CSV
    df = pd.read_csv(io.BytesIO(contents))
    
    required_columns = ["name", "email", "role"]
    if not all(col in df.columns for col in required_columns):
        raise HTTPException(400, f"Missing required columns: {required_columns}")
    
    success_count = 0
    failed_users = []
    
    for _, row in df.iterrows():
        try:
            # Check if user exists
            existing = await db.users.find_one({"email": row["email"]})
            
            if existing:
                failed_users.append({
                    "email": row["email"],
                    "error": "Email already exists"
                })
                continue
            
            # Create user
            password = row.get("password", "Welcome@123")
            hashed_pwd = pwd_context.hash(password)
            
            user_doc = {
                "_id": str(uuid4()),
                "name": row["name"],
                "email": row["email"],
                "password": hashed_pwd,
                "role": row["role"],
                "created_at": datetime.utcnow(),
                "is_active": True,
                "imported": True
            }
            
            await db.users.insert_one(user_doc)
            
            # Initialize stats for students
            if row["role"] == "student":
                await initialize_user_stats(db, user_doc["_id"])
            
            success_count += 1
            
        except Exception as e:
            failed_users.append({
                "email": row["email"],
                "error": str(e)
            })
    
    return {
        "message": f"Imported {success_count} users",
        "success_count": success_count,
        "failed_count": len(failed_users),
        "failed_users": failed_users
    }

@router.get("/users/export")
async def export_users(
    role: Optional[str] = None,
    format: str = Query("csv", regex="^(csv|json)$"),
    current_user: dict = Depends(require_role("admin"))
):
    """Export users data"""
    db = await get_db()
    
    # Build query
    query = {}
    if role:
        query["role"] = role
    
    # Get users
    users = await db.users.find(query, {"password": 0}).to_list(length=None)
    
    if format == "csv":
        # Convert to DataFrame
        df = pd.DataFrame(users)
        
        # Convert to CSV
        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)
        
        return StreamingResponse(
            iter([buffer.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=users_export.csv"}
        )
    else:  # JSON
        return {"users": users, "count": len(users)}
```

---

## Content Oversight

### Content Moderation

```python
@router.get("/content/overview")
async def get_content_overview(
    current_user: dict = Depends(require_role("admin"))
):
    """Get content overview for moderation"""
    db = await get_db()
    
    # Get assessment statistics
    assessments_by_type = await db.assessments.aggregate([
        {
            "$group": {
                "_id": "$type",
                "count": {"$sum": 1},
                "active": {
                    "$sum": {"$cond": ["$is_active", 1, 0]}
                }
            }
        }
    ]).to_list(length=None)
    
    # Get AI-generated content stats
    ai_questions = await db.ai_questions.count_documents({})
    ai_problems = await db.coding_problems.count_documents({
        "created_by": "AI"
    })
    
    # Get flagged content (if exists)
    flagged_content = await db.flagged_content.count_documents({
        "resolved": False
    })
    
    return {
        "assessments": {
            "by_type": assessments_by_type,
            "total": await db.assessments.count_documents({})
        },
        "ai_generated": {
            "questions": ai_questions,
            "coding_problems": ai_problems
        },
        "moderation": {
            "flagged_items": flagged_content
        }
    }

@router.post("/content/{content_id}/approve")
async def approve_content(
    content_id: str,
    content_type: str,
    current_user: dict = Depends(require_role("admin"))
):
    """Approve content for publication"""
    db = await get_db()
    
    collection_map = {
        "assessment": "assessments",
        "problem": "coding_problems",
        "question": "ai_questions"
    }
    
    collection = collection_map.get(content_type)
    if not collection:
        raise HTTPException(400, "Invalid content type")
    
    result = await db[collection].update_one(
        {"_id": ObjectId(content_id)},
        {
            "$set": {
                "approved": True,
                "approved_by": current_user["_id"],
                "approved_at": datetime.utcnow()
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(404, "Content not found")
    
    return {"message": "Content approved"}
```

---

## Summary

### Admin Features Matrix

| Feature | Endpoint | Description |
|---------|----------|-------------|
| Platform Analytics | `GET /admin/analytics/platform` | Overall statistics |
| User Management | `GET/POST/PUT/DELETE /admin/users` | CRUD operations |
| System Health | `GET /health/comprehensive` | Health monitoring |
| Bulk Import | `POST /admin/users/bulk-import` | CSV import |
| Export Users | `GET /admin/users/export` | CSV/JSON export |
| Content Overview | `GET /admin/content/overview` | Content statistics |
| Password Reset | `POST /admin/users/{id}/reset-password` | Reset passwords |

### Key Responsibilities

1. **Platform Monitoring** - Track usage, performance, and health
2. **User Administration** - Manage all user accounts
3. **System Maintenance** - Monitor and maintain system health
4. **Data Management** - Import/export and backup operations
5. **Content Moderation** - Review and approve content
6. **Analytics** - Platform-wide insights and reporting

---

**[Back to Features Overview](./FEATURES_OVERVIEW.md)**


