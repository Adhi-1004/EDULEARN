"""
API v1 package
Contains all versioned API endpoints
"""
from fastapi import APIRouter
from .auth import router as auth_router
from .users import router as users_router
from .admin import router as admin_router
from .teacher import router as teacher_router
from .assessments import router as assessments_router
from .coding import router as coding_router
from .notifications import router as notifications_router

# Create main API router
api_router = APIRouter(prefix="/api/v1")

# Include all routers
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(admin_router, prefix="/admin", tags=["Admin"])
api_router.include_router(teacher_router, prefix="/teacher", tags=["Teacher"])
api_router.include_router(assessments_router, prefix="/assessments", tags=["Assessments"])
api_router.include_router(coding_router, prefix="/coding", tags=["Coding"])
api_router.include_router(notifications_router, prefix="/notifications", tags=["Notifications"])

__all__ = ["api_router"]
