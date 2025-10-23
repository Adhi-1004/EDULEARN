"""
Notifications API endpoints
Handles notification creation, retrieval, and management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import List, Optional
from datetime import datetime

from ..db import get_db
from ..models.models import NotificationModel
from ..dependencies import get_current_user

router = APIRouter(tags=["notifications"])

async def create_assessment_completion_notification(
    db: AsyncIOMotorDatabase,
    student_id: str,
    assessment_title: str,
    score: float,
    teacher_id: str = None
):
    """Create notification for assessment completion"""
    try:
        # Create notification for the student
        student_notification = {
            "user_id": student_id,
            "type": "success",
            "title": "Assessment Completed",
            "message": f"You completed '{assessment_title}' with a score of {score:.1f}%",
            "priority": "normal",
            "is_read": False,
            "created_at": datetime.utcnow(),
            "read_at": None
        }
        
        await db.notifications.insert_one(student_notification)
        
        # Create notification for the teacher if teacher_id is provided
        if teacher_id:
            teacher_notification = {
                "user_id": teacher_id,
                "type": "info",
                "title": "Student Assessment Completed",
                "message": f"A student completed '{assessment_title}' with a score of {score:.1f}%",
                "priority": "normal",
                "is_read": False,
                "created_at": datetime.utcnow(),
                "read_at": None
            }
            
            await db.notifications.insert_one(teacher_notification)
        
        print(f"✅ [NOTIFICATIONS] Created assessment completion notifications for student {student_id}")
        
    except Exception as e:
        print(f"❌ [NOTIFICATIONS] Failed to create assessment completion notification: {str(e)}")

@router.get("/")
async def get_notifications(
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get all notifications for the current user.
    """
    try:
        print(f"🔔 [NOTIFICATIONS] Fetching notifications for user: {current_user.email} (ID: {current_user.id})")
        user_id = current_user.id
        
        # Try both user_id and student_id fields
        notifications = await db.notifications.find(
            {"$or": [
                {"user_id": ObjectId(user_id)},
                {"student_id": str(user_id)},
                {"user_id": str(user_id)}
            ]}
        ).sort("created_at", -1).to_list(length=100)
        
        print(f"📊 [NOTIFICATIONS] Found {len(notifications)} notifications for user {user_id}")
        
        # Log notification details
        for i, notification in enumerate(notifications):
            print(f"  📝 Notification {i+1}: {notification.get('title', 'No title')} - {notification.get('type', 'No type')}")
        
        # Convert ObjectId to string for JSON serialization and map fields
        for notification in notifications:
            # Convert all ObjectId fields to strings
            for key, value in notification.items():
                if isinstance(value, ObjectId):
                    notification[key] = str(value)
            
            # Map specific fields for frontend compatibility
            notification["id"] = str(notification["_id"])
            if "user_id" in notification:
                notification["user_id"] = str(notification["user_id"])
            
            # Map 'read' to 'is_read' for frontend compatibility
            if "read" in notification:
                notification["is_read"] = notification["read"]
                del notification["read"]
        
        return {
            "notifications": notifications,
            "unread_count": len([n for n in notifications if not n.get("is_read", False)])
        }
    except Exception as e:
        print(f"[ERROR] [NOTIFICATIONS] Failed to get notifications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve notifications"
        )

@router.post("/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Mark a notification as read.
    """
    try:
        user_id = current_user.id
        result = await db.notifications.update_one(
            {"_id": ObjectId(notification_id), "user_id": ObjectId(user_id)},
            {"$set": {"read": True}}
        )

        if result.modified_count == 1:
            return {"message": "Notification marked as read"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
    except Exception as e:
        print(f"[ERROR] [NOTIFICATIONS] Failed to mark notification as read: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark notification as read"
        )

@router.post("/mark-all-read")
async def mark_all_notifications_as_read(
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Mark all notifications as read for the current user.
    """
    try:
        user_id = current_user.id
        result = await db.notifications.update_many(
            {"user_id": ObjectId(user_id), "read": False},
            {"$set": {"read": True}}
        )

        return {
            "message": f"Marked {result.modified_count} notifications as read"
        }
    except Exception as e:
        print(f"[ERROR] [NOTIFICATIONS] Failed to mark all notifications as read: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark all notifications as read"
        )

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Delete a notification.
    """
    try:
        user_id = current_user.id
        result = await db.notifications.delete_one(
            {"_id": ObjectId(notification_id), "user_id": ObjectId(user_id)}
        )

        if result.deleted_count == 1:
            return {"message": "Notification deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
    except Exception as e:
        print(f"[ERROR] [NOTIFICATIONS] Failed to delete notification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete notification"
        )

@router.get("/unread-count")
async def get_unread_count(
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get the count of unread notifications for the current user.
    """
    try:
        user_id = current_user.id
        count = await db.notifications.count_documents(
            {"user_id": ObjectId(user_id), "read": False}
        )
        
        return {"unread_count": count}
    except Exception as e:
        print(f"[ERROR] [NOTIFICATIONS] Failed to get unread count: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get unread count"
        )

# Helper function to create notifications (used by other modules)
async def create_notification(
    db: AsyncIOMotorDatabase,
    user_id: str,
    message: str,
    notification_type: str = "general",
    related_id: Optional[str] = None
):
    """
    Helper function to create a notification.
    Used by other modules to create notifications.
    """
    try:
        notification_data = {
            "user_id": ObjectId(user_id),
            "message": message,
            "read": False,
            "timestamp": datetime.utcnow(),
            "notification_type": notification_type,
            "related_id": ObjectId(related_id) if related_id else None
        }
        
        result = await db.notifications.insert_one(notification_data)
        print(f"[SUCCESS] [NOTIFICATIONS] Created notification for user {user_id}: {message}")
        return str(result.inserted_id)
    except Exception as e:
        print(f"[ERROR] [NOTIFICATIONS] Failed to create notification: {str(e)}")
        return None
