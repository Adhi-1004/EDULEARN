"""
Topics and assessment configuration endpoints
Handles topic selection and assessment configuration
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import Dict, Any
from pydantic import BaseModel

from ..core.security import security_manager
from ..db import get_db
from ..dependencies import get_current_user
from ..models.models import UserModel

router = APIRouter()

# Response Models
class TopicResponse(BaseModel):
    topic: str
    qnCount: int
    difficulty: str

class AssessmentConfigResponse(BaseModel):
    success: bool
    topic: str
    qnCount: int
    difficulty: str
    error: str = None

@router.get("/", response_model=AssessmentConfigResponse)
async def get_assessment_config(
    current_user: UserModel = Depends(get_current_user)
):
    """Get assessment configuration for topic selection"""
    try:
        # For now, return a default configuration
        # In a real implementation, this would come from user preferences or AI
        return AssessmentConfigResponse(
            success=True,
            topic="Python Programming",
            qnCount=10,
            difficulty="medium"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get assessment configuration: {str(e)}"
        )

@router.get("/available", response_model=Dict[str, Any])
async def get_available_topics():
    """Get list of available topics for assessment"""
    try:
        topics = [
            {"name": "Python Programming", "difficulty": ["easy", "medium", "hard"]},
            {"name": "JavaScript", "difficulty": ["easy", "medium", "hard"]},
            {"name": "Data Structures", "difficulty": ["medium", "hard"]},
            {"name": "Algorithms", "difficulty": ["medium", "hard"]},
            {"name": "Web Development", "difficulty": ["easy", "medium"]},
            {"name": "Database Design", "difficulty": ["medium", "hard"]}
        ]
        
        return {
            "success": True,
            "topics": topics
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get available topics: {str(e)}"
        )
