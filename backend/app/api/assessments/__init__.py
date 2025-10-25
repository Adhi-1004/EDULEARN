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

# Create main router for the assessments module
router = APIRouter()

# --- CORRECTED ORDER ---
# Include routers with more specific paths FIRST

# 1. Submissions specific paths (like /student/upcoming, /{id}/submit)
router.include_router(submissions_router)

# 2. Teacher specific paths (like /{id}/publish - relative to teacher router's prefix)
#    Note: Ensure teacher_router itself has the correct prefix defined within teacher.py
#    If teacher.py defines routes relative to /assessments/teacher, include it like this:
router.include_router(teacher_router) # Assuming teacher_router internally has prefix="/teacher"

# 3. Notification specific paths
router.include_router(notifications_router)

# 4. Async specific paths
router.include_router(async_router)

# 5. Core/General paths LAST (like /{id}/details)
router.include_router(core_router)


# Export the main router
__all__ = ["router"]