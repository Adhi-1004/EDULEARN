"""
Coding API Module
Aggregates all coding-related routers
"""
from fastapi import APIRouter
from .problems import router as problems_router
from .execution import router as execution_router
from .submissions import router as submissions_router

# Create main router
router = APIRouter()

# Include all sub-routers
router.include_router(problems_router)
router.include_router(execution_router)
router.include_router(submissions_router)

# Export the main router
__all__ = ["router"]
