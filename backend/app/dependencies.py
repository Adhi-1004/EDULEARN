"""
Role-Based Access Control Dependencies
Provides security middleware for protecting API endpoints based on user roles
"""
from fastapi import Depends, HTTPException, status
from typing import Dict, Any, List
from .api.endpoints.auth import get_current_user
from .models.models import UserRole

# Role hierarchy: admin > teacher > student
ROLE_HIERARCHY = {
    "student": 1,
    "teacher": 2,
    "admin": 3
}

def has_role_or_higher(user_role: str, required_role: str) -> bool:
    """Check if user has required role or higher in hierarchy"""
    return ROLE_HIERARCHY.get(user_role, 0) >= ROLE_HIERARCHY.get(required_role, 0)

def require_role(required_role: str):
    """Create a dependency that requires a specific role or higher"""
    async def role_dependency(current_user: Dict[str, Any] = Depends(get_current_user)):
        user_role = current_user.get("role", "student")
        
        if not has_role_or_higher(user_role, required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires {required_role} privileges or higher. Your role: {user_role}"
            )
        
        return current_user
    
    return role_dependency

# Specific role dependencies
require_student = require_role("student")
require_teacher = require_role("teacher")
require_admin = require_role("admin")

# Multiple role dependencies
def require_any_role(allowed_roles: List[str]):
    """Create a dependency that requires any of the specified roles"""
    async def role_dependency(current_user: Dict[str, Any] = Depends(get_current_user)):
        user_role = current_user.get("role", "student")
        
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires one of the following roles: {', '.join(allowed_roles)}. Your role: {user_role}"
            )
        
        return current_user
    
    return role_dependency

# Common role combinations
require_teacher_or_admin = require_any_role(["teacher", "admin"])
require_admin_only = require_any_role(["admin"])

# Utility functions for role checking
def is_admin(user: Dict[str, Any]) -> bool:
    """Check if user is admin"""
    return user.get("role") == "admin"

def is_teacher_or_admin(user: Dict[str, Any]) -> bool:
    """Check if user is teacher or admin"""
    role = user.get("role")
    return role in ["teacher", "admin"]

def is_student(user: Dict[str, Any]) -> bool:
    """Check if user is student"""
    return user.get("role") == "student"

def can_manage_users(user: Dict[str, Any]) -> bool:
    """Check if user can manage other users (admin only)"""
    return is_admin(user)

def can_create_assessments(user: Dict[str, Any]) -> bool:
    """Check if user can create assessments (teacher or admin)"""
    return is_teacher_or_admin(user)

def can_view_analytics(user: Dict[str, Any]) -> bool:
    """Check if user can view analytics (teacher or admin)"""
    return is_teacher_or_admin(user)

def can_access_coding_platform(user: Dict[str, Any]) -> bool:
    """Check if user can access coding platform (all roles)"""
    return True  # All authenticated users can access coding platform

def can_submit_solutions(user: Dict[str, Any]) -> bool:
    """Check if user can submit coding solutions (all roles)"""
    return True  # All authenticated users can submit solutions

# Specific action-based dependencies
async def require_batch_management(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Require teacher or admin role for batch management"""
    user_role = current_user.get("role", "student")
    if user_role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Batch management requires teacher or admin privileges"
        )
    return current_user

async def require_user_management(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Require admin role for user management"""
    user_role = current_user.get("role", "student")
    if user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User management requires admin privileges"
        )
    return current_user

async def require_assessment_creation(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Require teacher or admin role for assessment creation"""
    user_role = current_user.get("role", "student")
    if user_role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Assessment creation requires teacher or admin privileges"
        )
    return current_user

async def require_analytics_access(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Require teacher or admin role for analytics access"""
    user_role = current_user.get("role", "student")
    if user_role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Analytics access requires teacher or admin privileges"
        )
    return current_user

async def require_platform_management(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Require admin role for platform management"""
    user_role = current_user.get("role", "student")
    if user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Platform management requires admin privileges"
        )
    return current_user

async def require_content_management(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Require teacher or admin role for content management"""
    user_role = current_user.get("role", "student")
    if user_role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Content management requires teacher or admin privileges"
        )
    return current_user
