from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from dotenv import load_dotenv
import os
from datetime import datetime

from database import init_db, get_db
from routers import auth, users, questions, results, coding, code_execution
from models.schemas import AssessmentConfig

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        print("🚀 Starting FastAPI Backend...")
        print(f"🔧 Environment check:")
        print(f"   - MONGO_URI: {'Set' if os.getenv('MONGO_URI') else 'Not set'}")
        print(f"   - DB_NAME: {'Set' if os.getenv('DB_NAME') else 'Not set'}")
        print(f"   - SECRET_KEY: {'Set' if os.getenv('SECRET_KEY') else 'Not set'}")
        
        await init_db()
        print("🚀 FastAPI Backend Started Successfully")
    except Exception as e:
        print(f"❌ Startup Error: {str(e)}")
        import traceback
        print(f"❌ Startup Traceback: {traceback.format_exc()}")
        raise e
    yield
    # Shutdown
    print("🛑 FastAPI Backend Shutdown")

app = FastAPI(
    title="modLRN API",
    description="AI-powered Adaptive Learning Platform API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://127.0.0.1:5173", 
        "http://localhost:3000",
        "https://modlrn.vercel.app",  # Production frontend
        "https://modlrn.onrender.com",  # Production backend
        "https://accounts.google.com",  # Google OAuth
        "https://oauth2.googleapis.com"  # Google OAuth token endpoint
    ],
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