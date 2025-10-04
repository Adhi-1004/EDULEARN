"""
Authentication endpoints
Handles login, logout, token refresh, and user authentication
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr

from ...core.security import security_manager
from ...db import get_db
from ...schemas.schemas import UserCreate, UserResponse
from ...models.models import UserModel
from ...utils.auth_utils import verify_password, get_password_hash

router = APIRouter()
security = HTTPBearer()

# Request/Response Models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
    expires_in: int

class TokenRefreshRequest(BaseModel):
    refresh_token: str

class TokenRefreshResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    """Authenticate user and return access token"""
    try:
        db = await get_db()
        
        # Find user by email
        user_doc = await db.users.find_one({"email": login_data.email})
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(login_data.password, user_doc["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Create access token
        access_token = security_manager.create_access_token(
            data={"sub": str(user_doc["_id"]), "email": user_doc["email"], "role": user_doc.get("role", "student")}
        )
        
        # Update last login
        await db.users.update_one(
            {"_id": user_doc["_id"]},
            {"$set": {"last_login": datetime.utcnow()}}
        )
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(**{k: v for k, v in user_doc.items() if k != "password"}),
            expires_in=security_manager.access_token_expire_minutes * 60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    """Register a new user"""
    try:
        db = await get_db()
        
        # Check if user already exists
        existing_user = await db.users.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = get_password_hash(user_data.password)
        
        # Create user document
        user_doc = {
            "username": user_data.username,
            "email": user_data.email,
            "password": hashed_password,
            "role": user_data.role,
            "created_at": datetime.utcnow(),
            "last_login": None,
            "is_active": True
        }
        
        # Insert user
        result = await db.users.insert_one(user_doc)
        user_doc["_id"] = result.inserted_id
        
        return UserResponse(**{k: v for k, v in user_doc.items() if k != "password"})
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh_token(refresh_data: TokenRefreshRequest):
    """Refresh access token"""
    try:
        # Verify refresh token
        payload = security_manager.verify_token(
            HTTPAuthorizationCredentials(scheme="bearer", credentials=refresh_data.refresh_token)
        )
        
        # Create new access token
        access_token = security_manager.create_access_token(
            data={"sub": payload["sub"], "email": payload.get("email"), "role": payload.get("role")}
        )
        
        return TokenRefreshResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=security_manager.access_token_expire_minutes * 60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    try:
        user_id = security_manager.get_current_user_id(credentials)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        
        db = await get_db()
        user_doc = await db.users.find_one({"_id": user_id})
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(**{k: v for k, v in user_doc.items() if k != "password"})
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user: {str(e)}"
        )

@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Logout user (client should discard token)"""
    return {"message": "Successfully logged out"}
