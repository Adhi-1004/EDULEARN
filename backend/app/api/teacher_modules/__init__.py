"""
Teacher API Module
Aggregates all teacher-related routers
"""
from fastapi import APIRouter
from .batches import router as batches_router
from .students import router as students_router
from .student_edit import router as student_edit_router
from .assessments import router as assessments_router
from .reports import router as reports_router

# Create main router
router = APIRouter()

# Include all sub-routers
router.include_router(batches_router)
router.include_router(students_router)
router.include_router(student_edit_router)
router.include_router(assessments_router)
router.include_router(reports_router)

# Export the main router
__all__ = ["router"]
