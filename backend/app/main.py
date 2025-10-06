"""
FastAPI application entry point
Main application configuration and startup
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from datetime import datetime

from .core.config import settings
from .core.security import security_manager
from .db import init_db, get_db
from .api import api_router

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

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
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

# Include API router
app.include_router(api_router)

# Backward compatibility routes (for frontend)
from .api.auth import router as auth_router
from .api.users import router as users_router
from .api.admin import router as admin_router
from .api.teacher import router as teacher_router
from .api.assessments import router as assessments_router
from .api.coding import router as coding_router
from .api.notifications import router as notifications_router
from .api.results import router as results_router
from .api.topics import router as topics_router

# Include backward compatibility routes (without /api prefix)
app.include_router(auth_router, prefix="/auth", tags=["Authentication (Legacy)"])
app.include_router(users_router, prefix="/users", tags=["Users (Legacy)"])
app.include_router(admin_router, prefix="/admin", tags=["Admin (Legacy)"])
app.include_router(teacher_router, prefix="/teacher", tags=["Teacher (Legacy)"])
app.include_router(assessments_router, prefix="/assessments", tags=["Assessments (Legacy)"])
app.include_router(coding_router, prefix="/coding", tags=["Coding (Legacy)"])
app.include_router(notifications_router, prefix="/notifications", tags=["Notifications (Legacy)"])
app.include_router(results_router, prefix="/results", tags=["Results (Legacy)"])
app.include_router(topics_router, prefix="/topics", tags=["Topics (Legacy)"])

# Add /db/questions endpoint for backward compatibility
@app.get("/db/questions")
async def get_questions_from_db(
    topic: str = "Python Programming",
    difficulty: str = "medium", 
    count: int = 10
):
    """Generate AI-powered MCQ questions - always generate unique questions"""
    try:
        from app.services.gemini_coding_service import gemini_coding_service
        
        print(f"🤖 [QUESTIONS] Generating {count} unique {difficulty} questions for topic: {topic}")
        
        # Always generate fresh questions using Gemini AI
        questions = await gemini_coding_service.generate_mcq_questions(
            topic=topic,
            difficulty=difficulty,
            count=count
        )
        
        # Transform questions to convert letter answers to actual option text
        transformed_questions = []
        for question in questions:
            # Convert letter answer (A, B, C, D) to actual option text
            answer_letter = question.get("answer", "")
            options = question.get("options", [])
            
            # Convert letter to index (A=0, B=1, C=2, D=3)
            if answer_letter in ["A", "B", "C", "D"]:
                answer_index = ord(answer_letter) - ord("A")
                if answer_index < len(options):
                    question["answer"] = options[answer_index]
                    question["correct_answer"] = answer_index  # Add correct_answer field for frontend
                else:
                    question["answer"] = options[0] if options else ""
                    question["correct_answer"] = 0
            else:
                # If answer is already text, keep it as is
                question["correct_answer"] = -1  # No index available
            
            transformed_questions.append(question)
        
        print(f"✅ [QUESTIONS] Generated {len(transformed_questions)} questions successfully")
        return transformed_questions
        
    except Exception as e:
        print(f"❌ [QUESTIONS] Error generating questions: {str(e)}")
        # Fallback to mock data if AI fails
        mock_questions = []
        for i in range(count):
            correct_index = i % 4
            question = {
                "id": f"q{i+1}",
                "question": f"Sample question {i+1} about {topic}",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "answer": f"Option {chr(65 + correct_index)}",  # Actual option text
                "correct_answer": correct_index,  # Index of correct answer
                "explanation": f"This is the explanation for question {i+1}",
                "difficulty": difficulty,
                "topic": topic
            }
            mock_questions.append(question)
        return mock_questions

# Health check endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "modLRN API is running",
        "version": settings.app_version,
        "status": "healthy"
    }

@app.get("/health")
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
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.app_version
    }

@app.get("/api/health")
async def api_health():
    """API health check"""
    return {
        "success": True,
        "status": "healthy",
        "message": "API is running",
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
        "app.main:app",
        host="0.0.0.0",
        port=5001,
        reload=True
    )