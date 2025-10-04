"""
Reset admin user endpoint
"""
from fastapi import APIRouter, HTTPException
from ..db.mock_db import mock_db
from ..models.models import UserModel
from ..utils.auth_utils import create_access_token

router = APIRouter()

@router.post("/reset-admin")
async def reset_admin_user():
    """Reset admin user with known credentials"""
    try:
        print("[RESET] Clearing existing users...")
        # Clear all users
        mock_db.data['users'] = []
        
        print("[RESET] Creating new admin user...")
        # Create fresh admin user
        admin_user = {
            "username": "Adhithya",
            "email": "adhiadmin@gmail.com",
            "password": UserModel.hash_password("admin123"),
            "is_admin": True,
            "role": "admin",
            "name": "Adhithya Admin",
            "profile_picture": None,
            "face_descriptor": None,
            # Gamification fields
            "xp": 0,
            "level": 1,
            "streak": 0,
            "longest_streak": 0,
            "badges": [],
            "last_activity": None,
            "total_questions_answered": 0,
            "correct_answers": 0,
            "perfect_scores": 0,
            "consecutive_days": 0
        }
        
        # Insert admin user
        result = await mock_db.insert_one(admin_user)
        admin_user['_id'] = result['inserted_id']
        
        # Create access token
        access_token = create_access_token(
            data={
                "sub": str(admin_user['_id']),
                "email": admin_user['email'],
                "role": admin_user['role']
            }
        )
        
        print(f"[SUCCESS] Admin user reset successfully!")
        
        return {
            "success": True,
            "message": "Admin user reset successfully",
            "access_token": access_token,
            "user": {
                "id": str(admin_user['_id']),
                "email": admin_user['email'],
                "username": admin_user['username'],
                "name": admin_user['name'],
                "role": admin_user['role'],
                "is_admin": admin_user['is_admin']
            },
            "login_credentials": {
                "email": "adhiadmin@gmail.com",
                "password": "admin123"
            }
        }
        
    except Exception as e:
        print(f"[ERROR] Failed to reset admin user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to reset admin user: {str(e)}")
