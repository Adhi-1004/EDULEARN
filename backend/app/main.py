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
from .api.v1 import api_router

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