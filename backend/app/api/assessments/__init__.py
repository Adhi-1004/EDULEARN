"""
Assessments API Module
Aggregates all assessment-related routers
"""
from fastapi import APIRouter
from .core import router as core_router
from .submissions import router as submissions_router
from .teacher import router as teacher_router
from .notifications import router as notifications_router
from .async_endpoints import router as async_router

# Create main router
router = APIRouter()

# Include all sub-routers
router.include_router(core_router)
router.include_router(submissions_router)
router.include_router(teacher_router)
router.include_router(notifications_router)
router.include_router(async_router)

# Export the main router
__all__ = ["router"]
