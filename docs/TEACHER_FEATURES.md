# 👨‍🏫 Teacher Management Features

## Table of Contents
1. [Overview](#overview)
2. [Teacher Dashboard](#teacher-dashboard)
3. [Batch Management](#batch-management)
4. [Student Management](#student-management)
5. [Performance Analytics](#performance-analytics)
6. [AI-Powered Reports](#ai-powered-reports)
7. [Bulk Student Operations](#bulk-student-operations)

---

## Overview

The Teacher Management System provides comprehensive tools for classroom management, student monitoring, and performance analytics.

### Key Capabilities
- 📊 Real-time dashboard analytics
- 👥 Batch creation and management
- 📈 Student performance tracking
- 🤖 AI-generated student reports
- 📥 Bulk student import/export
- 📝 Assessment creation and management
- 🎯 Individual student feedback

---

## Teacher Dashboard

### Feature Overview
Centralized dashboard displaying key metrics, upcoming assessments, recent activity, and batch statistics.

### Dashboard Flow

####Process Diagram
```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Teacher    │    │   Frontend   │    │   Backend    │    │   Database   │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │                   │
       │ Access Dashboard  │                   │                   │
       ├──────────────────▶│                   │                   │
       │                   │                   │                   │
       │                   │ GET /teacher/     │                   │
       │                   │     dashboard     │                   │
       │                   ├──────────────────▶│                   │
       │                   │                   │                   │
       │                   │                   │ 1. Get Batches    │
       │                   │                   ├──────────────────▶│
       │                   │                   │                   │
       │                   │                   │ 2. Get Students   │
       │                   │                   ├──────────────────▶│
       │                   │                   │                   │
       │                   │                   │ 3. Get Assessments│
       │                   │                   ├──────────────────▶│
       │                   │                   │                   │
       │                   │                   │ 4. Get Submissions│
       │                   │                   ├──────────────────▶│
       │                   │                   │                   │
       │                   │                   │ 5. Calculate Stats│
       │                   │                   ├───────┐           │
       │                   │                   │       │           │
       │                   │                   │◀──────┘           │
       │                   │                   │                   │
       │                   │ 6. Dashboard Data │                   │
       │                   │◀──────────────────┤                   │
       │                   │                   │                   │
       │ 7. Display        │                   │                   │
       │    Dashboard      │                   │                   │
       │◀──────────────────┤                   │                   │
       │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼
```

#### Files Involved

**Frontend:**
- `frontend/src/pages/teacher/Dashboard.tsx`
- `frontend/src/components/teacher/DashboardCard.tsx`
- `frontend/src/api/teacherService.ts`

**Backend:**
- `backend/app/api/teacher.py`
  - Endpoint: `GET /api/teacher/dashboard`

#### Implementation

```python
# File: backend/app/api/teacher.py
@router.get("/dashboard")
async def teacher_dashboard(
    current_user: UserModel = Depends(require_role("teacher"))
):
    """Get teacher dashboard overview"""
    db = await get_db()
    teacher_id = str(current_user.id)
    
    # Get batches count
    batches = await db.batches.count_documents({"teacher_id": teacher_id})
    
    # Get students count
    students = await db.users.count_documents({
        "batch_id": {"$in": await get_teacher_batch_ids(db, teacher_id)},
        "role": "student"
    })
    
    # Get assessments count
    assessments = await db.assessments.count_documents({
        "created_by": teacher_id
    })
    
    # Get recent submissions
    recent_submissions = await db.assessment_submissions.find({
        "assessment_id": {"$in": await get_teacher_assessment_ids(db, teacher_id)}
    }).sort("submitted_at", -1).limit(10).to_list(length=10)
    
    # Calculate average performance
    avg_score = 0
    if recent_submissions:
        avg_score = sum(s["percentage"] for s in recent_submissions) / len(recent_submissions)
    
    return {
        "total_batches": batches,
        "total_students": students,
        "total_assessments": assessments,
        "recent_submissions": len(recent_submissions),
        "average_performance": round(avg_score, 2),
        "recent_activity": recent_submissions[:5]
    }
```

#### Dashboard Components

```typescript
// File: frontend/src/pages/teacher/Dashboard.tsx
const TeacherDashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState(null);
  
  useEffect(() => {
    loadDashboard();
  }, []);
  
  const loadDashboard = async () => {
    const data = await teacherService.getDashboard();
    setDashboardData(data);
  };
  
  return (
    <div className="dashboard-grid">
      <DashboardCard
        title="Total Batches"
        value={dashboardData?.total_batches}
        icon={<BatchIcon />}
        color="blue"
      />
      <DashboardCard
        title="Total Students"
        value={dashboardData?.total_students}
        icon={<StudentIcon />}
        color="green"
      />
      <DashboardCard
        title="Assessments"
        value={dashboardData?.total_assessments}
        icon={<AssessmentIcon />}
        color="purple"
      />
      <DashboardCard
        title="Avg Performance"
        value={`${dashboardData?.average_performance}%`}
        icon={<PerformanceIcon />}
        color="orange"
      />
      
      <RecentActivity activities={dashboardData?.recent_activity} />
    </div>
  );
};
```

---

## Batch Management

### Feature Overview
Teachers can create and manage batches (classes/groups) of students for organized assessment assignment.

### Create Batch Flow

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Teacher    │    │   Frontend   │    │   Backend    │    │   Database   │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │                   │
       │ 1. Create Batch   │                   │                   │
       │    Form:          │                   │                   │
       │    - Name         │                   │                   │
       │    - Description  │                   │                   │
       │    - Start/End    │                   │                   │
       ├──────────────────▶│                   │                   │
       │                   │                   │                   │
       │                   │ 2. POST /teacher/ │                   │
       │                   │    batches        │                   │
       │                   ├──────────────────▶│                   │
       │                   │                   │                   │
       │                   │                   │ 3. Create Batch   │
       │                   │                   │    Document       │
       │                   │                   ├──────────────────▶│
       │                   │                   │                   │
       │                   │ 4. Batch Created  │                   │
       │                   │◀──────────────────┤                   │
       │                   │                   │                   │
       │ 5. Show Success   │                   │                   │
       │◀──────────────────┤                   │                   │
       │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼
```

#### Implementation

```python
# File: backend/app/api/teacher.py
@router.post("/batches")
async def create_batch(
    batch_data: BatchCreate,
    current_user: UserModel = Depends(require_role("teacher"))
):
    """Create a new batch"""
    db = await get_db()
    
    batch_doc = {
        "_id": str(uuid4()),
        "name": batch_data.name,
        "description": batch_data.description,
        "teacher_id": str(current_user.id),
        "teacher_name": current_user.name,
        "created_at": datetime.utcnow(),
        "start_date": batch_data.start_date,
        "end_date": batch_data.end_date,
        "is_active": True,
        "student_count": 0
    }
    
    await db.batches.insert_one(batch_doc)
    
    return {
        "message": "Batch created successfully",
        "batch_id": batch_doc["_id"],
        "name": batch_doc["name"]
    }

@router.get("/batches")
async def get_batches(
    current_user: UserModel = Depends(require_role("teacher"))
):
    """Get all batches for current teacher"""
    db = await get_db()
    
    batches = await db.batches.find({
        "teacher_id": str(current_user.id),
        "is_active": True
    }).to_list(length=None)
    
    # Enrich with student count
    for batch in batches:
        student_count = await db.users.count_documents({
            "batch_id": batch["_id"],
            "role": "student"
        })
        batch["student_count"] = student_count
    
    return batches

@router.delete("/batches/{batch_id}")
async def delete_batch(
    batch_id: str,
    current_user: UserModel = Depends(require_role("teacher"))
):
    """Delete a batch and unassign students"""
    db = await get_db()
    
    # Verify ownership
    batch = await db.batches.find_one({
        "_id": batch_id,
        "teacher_id": str(current_user.id)
    })
    
    if not batch:
        raise HTTPException(404, "Batch not found")
    
    # Unassign students
    await db.users.update_many(
        {"batch_id": batch_id},
        {"$set": {"batch_id": None}}
    )
    
    # Mark batch as inactive
    await db.batches.update_one(
        {"_id": batch_id},
        {"$set": {"is_active": False}}
    )
    
    return {"message": "Batch deleted successfully"}
```

---

## Student Management

### Feature Overview
Add students individually or in bulk, assign to batches, view performance, and provide feedback.

### Add Individual Student

```python
@router.post("/students/add")
async def add_student(
    student_data: StudentAdd,
    current_user: UserModel = Depends(require_role("teacher"))
):
    """Add a student to a batch"""
    db = await get_db()
    
    # Verify batch ownership
    batch = await db.batches.find_one({
        "_id": student_data.batch_id,
        "teacher_id": str(current_user.id)
    })
    
    if not batch:
        raise HTTPException(403, "Invalid batch or unauthorized")
    
    # Check if user exists
    user = await db.users.find_one({"email": student_data.email})
    
    if user:
        # Update existing user
        await db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {"batch_id": student_data.batch_id}}
        )
        user_id = user["_id"]
    else:
        # Create new user
        hashed_pwd = pwd_context.hash(student_data.password or "Student@123")
        
        user_doc = {
            "_id": str(uuid4()),
            "name": student_data.name,
            "email": student_data.email,
            "password": hashed_pwd,
            "role": "student",
            "batch_id": student_data.batch_id,
            "created_at": datetime.utcnow(),
            "is_active": True
        }
        
        await db.users.insert_one(user_doc)
        user_id = user_doc["_id"]
        
        # Initialize gamification
        await initialize_user_stats(db, user_id)
    
    return {
        "message": "Student added successfully",
        "user_id": user_id
    }

@router.post("/students/remove")
async def remove_student(
    student_id: str,
    batch_id: str,
    current_user: UserModel = Depends(require_role("teacher"))
):
    """Remove student from batch"""
    db = await get_db()
    
    # Verify batch ownership
    batch = await db.batches.find_one({
        "_id": batch_id,
        "teacher_id": str(current_user.id)
    })
    
    if not batch:
        raise HTTPException(403, "Unauthorized")
    
    # Remove student from batch
    await db.users.update_one(
        {"_id": student_id, "batch_id": batch_id},
        {"$set": {"batch_id": None}}
    )
    
    return {"message": "Student removed from batch"}
```

### Get Students with Performance

```python
@router.get("/students")
async def get_students(
    batch_id: Optional[str] = None,
    current_user: UserModel = Depends(require_role("teacher"))
):
    """Get all students, optionally filtered by batch"""
    db = await get_db()
    
    # Build query
    query = {"role": "student"}
    
    if batch_id:
        # Verify batch ownership
        batch = await db.batches.find_one({
            "_id": batch_id,
            "teacher_id": str(current_user.id)
        })
        if not batch:
            raise HTTPException(403, "Unauthorized")
        query["batch_id"] = batch_id
    else:
        # Get all batches for teacher
        teacher_batches = await db.batches.find({
            "teacher_id": str(current_user.id)
        }).to_list(length=None)
        batch_ids = [b["_id"] for b in teacher_batches]
        query["batch_id"] = {"$in": batch_ids}
    
    students = await db.users.find(query).to_list(length=None)
    
    # Enrich with performance data
    for student in students:
        # Get submissions count
        submissions = await db.assessment_submissions.count_documents({
            "student_id": student["_id"]
        })
        
        # Get average score
        results = await db.assessment_submissions.find({
            "student_id": student["_id"]
        }).to_list(length=None)
        
        avg_score = 0
        if results:
            avg_score = sum(r["percentage"] for r in results) / len(results)
        
        student["performance"] = {
            "assessments_taken": submissions,
            "average_score": round(avg_score, 2)
        }
    
    return students
```

---

## Performance Analytics

### Feature Overview
Comprehensive analytics dashboard showing student performance, assessment statistics, and trends.

```python
@router.get("/analytics/overview")
async def get_analytics(
    current_user: UserModel = Depends(require_role("teacher"))
):
    """Get comprehensive analytics overview"""
    db = await get_db()
    teacher_id = str(current_user.id)
    
    # Get all teacher's batches
    batches = await db.batches.find({
        "teacher_id": teacher_id
    }).to_list(length=None)
    batch_ids = [b["_id"] for b in batches]
    
    # Get all students in batches
    students = await db.users.find({
        "batch_id": {"$in": batch_ids},
        "role": "student"
    }).to_list(length=None)
    student_ids = [s["_id"] for s in students]
    
    # Get all submissions
    submissions = await db.assessment_submissions.find({
        "student_id": {"$in": student_ids}
    }).to_list(length=None)
    
    # Calculate statistics
    total_submissions = len(submissions)
    avg_score = sum(s["percentage"] for s in submissions) / total_submissions if submissions else 0
    
    # Performance distribution
    excellent = len([s for s in submissions if s["percentage"] >= 90])
    good = len([s for s in submissions if 75 <= s["percentage"] < 90])
    average = len([s for s in submissions if 50 <= s["percentage"] < 75])
    poor = len([s for s in submissions if s["percentage"] < 50])
    
    # Top performers
    student_scores = {}
    for submission in submissions:
        sid = submission["student_id"]
        if sid not in student_scores:
            student_scores[sid] = []
        student_scores[sid].append(submission["percentage"])
    
    top_students = []
    for sid, scores in student_scores.items():
        student = next((s for s in students if s["_id"] == sid), None)
        if student:
            top_students.append({
                "id": sid,
                "name": student["name"],
                "average_score": round(sum(scores) / len(scores), 2),
                "assessments_taken": len(scores)
            })
    
    top_students.sort(key=lambda x: x["average_score"], reverse=True)
    
    return {
        "overview": {
            "total_students": len(students),
            "total_batches": len(batches),
            "total_submissions": total_submissions,
            "average_score": round(avg_score, 2)
        },
        "performance_distribution": {
            "excellent": excellent,
            "good": good,
            "average": average,
            "poor": poor
        },
        "top_performers": top_students[:10],
        "recent_submissions": sorted(
            submissions,
            key=lambda x: x["submitted_at"],
            reverse=True
        )[:20]
    }
```

---

## AI-Powered Reports

### Feature Overview
Generate comprehensive AI-powered student performance reports using Google Gemini.

```python
# File: backend/app/api/teacher.py
@router.post("/generate-student-report")
async def generate_student_report(
    student_id: str,
    current_user: UserModel = Depends(require_role("teacher"))
):
    """Generate AI-powered student report"""
    db = await get_db()
    
    # Get student data
    student = await db.users.find_one({"_id": student_id})
    if not student:
        raise HTTPException(404, "Student not found")
    
    # Get student performance data
    submissions = await db.assessment_submissions.find({
        "student_id": student_id
    }).to_list(length=None)
    
    # Prepare data for AI
    performance_summary = {
        "total_assessments": len(submissions),
        "average_score": sum(s["percentage"] for s in submissions) / len(submissions) if submissions else 0,
        "best_score": max(s["percentage"] for s in submissions) if submissions else 0,
        "recent_trend": [s["percentage"] for s in submissions[-5:]]
    }
    
    # Generate report using Gemini
    gemini_service = GeminiCodingService()
    prompt = f"""
    Generate a comprehensive student performance report for {student['name']}.
    
    Performance Data:
    - Total Assessments: {performance_summary['total_assessments']}
    - Average Score: {performance_summary['average_score']:.2f}%
    - Best Score: {performance_summary['best_score']:.2f}%
    - Recent Trend: {performance_summary['recent_trend']}
    
    Please provide:
    1. Overall Performance Summary
    2. Strengths and Weaknesses
    3. Recommendations for Improvement
    4. Learning Path Suggestions
    
    Keep the report professional and constructive.
    """
    
    response = gemini_service.model.generate_content(prompt)
    report_text = response.text
    
    # Save report
    report_doc = {
        "_id": str(uuid4()),
        "student_id": student_id,
        "teacher_id": str(current_user.id),
        "report_text": report_text,
        "performance_data": performance_summary,
        "generated_at": datetime.utcnow()
    }
    
    await db.student_reports.insert_one(report_doc)
    
    return {
        "report_id": report_doc["_id"],
        "report": report_text,
        "performance_summary": performance_summary
    }

@router.get("/students/{student_id}/detailed-report")
async def get_student_report(
    student_id: str,
    current_user: UserModel = Depends(require_role("teacher"))
):
    """Get detailed student report"""
    db = await get_db()
    
    # Get latest report
    report = await db.student_reports.find_one(
        {"student_id": student_id},
        sort=[("generated_at", -1)]
    )
    
    if not report:
        raise HTTPException(404, "No report found for this student")
    
    return report
```

---

## Bulk Student Operations

### Feature Overview
Import multiple students at once using Excel/CSV files.

### Bulk Import Flow

```python
# File: backend/app/api/bulk_students.py
@router.post("/upload")
async def upload_students(
    file: UploadFile,
    batch_id: str = Form(...),
    current_user: UserModel = Depends(require_role("teacher"))
):
    """Bulk upload students from Excel/CSV"""
    db = await get_db()
    
    # Verify batch ownership
    batch = await db.batches.find_one({
        "_id": batch_id,
        "teacher_id": str(current_user.id)
    })
    
    if not batch:
        raise HTTPException(403, "Invalid batch")
    
    # Read file
    contents = await file.read()
    
    # Parse Excel
    df = pd.read_excel(io.BytesIO(contents))
    
    required_columns = ["name", "email"]
    if not all(col in df.columns for col in required_columns):
        raise HTTPException(400, "Missing required columns")
    
    success_count = 0
    failed_students = []
    
    for _, row in df.iterrows():
        try:
            # Check if user exists
            existing = await db.users.find_one({"email": row["email"]})
            
            if existing:
                # Update batch
                await db.users.update_one(
                    {"_id": existing["_id"]},
                    {"$set": {"batch_id": batch_id}}
                )
            else:
                # Create new user
                password = row.get("password", "Student@123")
                hashed_pwd = pwd_context.hash(password)
                
                user_doc = {
                    "_id": str(uuid4()),
                    "name": row["name"],
                    "email": row["email"],
                    "password": hashed_pwd,
                    "role": "student",
                    "batch_id": batch_id,
                    "created_at": datetime.utcnow(),
                    "is_active": True
                }
                
                await db.users.insert_one(user_doc)
                await initialize_user_stats(db, user_doc["_id"])
            
            success_count += 1
        except Exception as e:
            failed_students.append({
                "name": row["name"],
                "email": row["email"],
                "error": str(e)
            })
    
    return {
        "message": f"Successfully imported {success_count} students",
        "success_count": success_count,
        "failed_count": len(failed_students),
        "failed_students": failed_students
    }

@router.get("/template")
async def download_template():
    """Download Excel template for bulk upload"""
    # Create sample DataFrame
    df = pd.DataFrame({
        "name": ["John Doe", "Jane Smith"],
        "email": ["john@example.com", "jane@example.com"],
        "password": ["optional", "optional"]
    })
    
    # Convert to Excel
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=student_template.xlsx"}
    )
```

---

## Summary

### Teacher Features Matrix

| Feature | Endpoint | Files | Key Functionality |
|---------|----------|-------|-------------------|
| Dashboard | `GET /teacher/dashboard` | `Dashboard.tsx`, `teacher.py` | Overview statistics |
| Create Batch | `POST /teacher/batches` | `BatchManagement.tsx` | Batch creation |
| Manage Students | `POST /teacher/students/add` | `StudentManagement.tsx` | Individual addition |
| Bulk Import | `POST /bulk-students/upload` | `BulkStudentUpload.tsx` | Excel/CSV import |
| Analytics | `GET /teacher/analytics/overview` | `TeacherAnalytics.tsx` | Performance insights |
| AI Reports | `POST /teacher/generate-student-report` | `StudentReport.tsx` | Gemini-powered reports |

### Database Collections

1. **batches** - Batch/class information
2. **users** - Students with batch assignments
3. **assessment_submissions** - Performance data
4. **student_reports** - AI-generated reports

---

**[Back to Features Overview](./FEATURES_OVERVIEW.md)** | **[Next: Admin Features →](./ADMIN_FEATURES.md)**

