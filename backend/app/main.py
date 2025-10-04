"""
FastAPI application entry point
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from datetime import datetime

from .core.config import settings
from .db import init_db, get_db
from .api.endpoints import auth, assessments
from .api import users, questions, results, coding, code_execution, teacher_dashboard, admin_dashboard, admin
from .api import enhanced_users, enhanced_teacher_dashboard, enhanced_admin_dashboard, reset_admin
from .schemas import AssessmentConfig

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    try:
        print("[STARTUP] Starting FastAPI Backend...")
        print(f"[ENV] Environment check:")
        print(f"   - MONGO_URI: {'Set' if settings.mongo_uri else 'Not set'}")
        print(f"   - DB_NAME: {'Set' if settings.db_name else 'Not set'}")
        print(f"   - SECRET_KEY: {'Set' if settings.secret_key else 'Not set'}")
        
        await init_db()
        print("[SUCCESS] FastAPI Backend Started Successfully")
    except Exception as e:
        print(f"[ERROR] Startup Error: {str(e)}")
        import traceback
        print(f"[ERROR] Startup Traceback: {traceback.format_exc()}")
        raise e
    yield
    # Shutdown
    print("[SHUTDOWN] FastAPI Backend Shutdown")

app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/db", tags=["Users"])
app.include_router(questions.router, prefix="/db", tags=["Questions"])
app.include_router(results.router, prefix="/api", tags=["Results"])
app.include_router(coding.router, prefix="/api/coding", tags=["Coding Platform"])
app.include_router(code_execution.router, prefix="/api/execute", tags=["Code Execution"])
app.include_router(teacher_dashboard.router, prefix="/api/teacher", tags=["Teacher Dashboard"])
app.include_router(admin_dashboard.router, prefix="/api/admin", tags=["Admin Dashboard"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin Management"])
app.include_router(assessments.router, prefix="/api/assessments", tags=["Assessments"])

# Enhanced routers with AI features
app.include_router(enhanced_users.router, tags=["Enhanced Users"])
app.include_router(enhanced_teacher_dashboard.router, tags=["Enhanced Teacher Dashboard"])
app.include_router(enhanced_admin_dashboard.router, tags=["Enhanced Admin Dashboard"])

# Admin reset endpoint
app.include_router(reset_admin.router, prefix="/api", tags=["Admin Reset"])

# Session storage for assessment configuration
assessment_sessions = {}

@app.post("/api/topic")
async def set_assessment_config(config: AssessmentConfig, user_id: str = Depends(auth.get_current_user_id)):
    """Set assessment configuration in session"""
    try:
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        session_key = f"assessment_{user_id}"
        assessment_sessions[session_key] = {
            "userId": user_id,
            "topic": config.topic,
            "qnCount": config.qnCount,
            "difficulty": config.difficulty
        }
        
        return {
            "success": True,
            "userId": user_id,
            "topic": config.topic,
            "qnCount": config.qnCount,
            "difficulty": config.difficulty
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/topic")
async def get_assessment_config(user_id: str = Depends(auth.get_current_user_id)):
    """Get assessment configuration from session"""
    try:
        if not user_id:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        session_key = f"assessment_{user_id}"
        config = assessment_sessions.get(session_key)
        
        if not config:
            raise HTTPException(status_code=404, detail="No assessment configuration found")
        
        return {
            "success": True,
            "userId": user_id,
            "topic": config["topic"],
            "qnCount": config["qnCount"],
            "difficulty": config["difficulty"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "modLRN API is running"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint for backend status"""
    try:
        # Test database connection
        db = await get_db()
        await db.command("ping")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy",
        "message": "Backend is running",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/test-db")
async def test_database():
    """Test database connection specifically"""
    try:
        db = await get_db()
        await db.command("ping")
        return {
            "success": True,
            "message": "Database connection successful",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Database connection failed: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5001,
        reload=True
    )