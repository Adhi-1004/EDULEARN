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

@router.get("/")
async def get_notifications(
    db: AsyncIOMotorDatabase = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get all notifications for the current user.
    """
    try:
        user_id = current_user.id
        notifications = await db.notifications.find(
            {"user_id": ObjectId(user_id)}
        ).sort("timestamp", -1).to_list(length=100)
        
        # Convert ObjectId to string for JSON serialization
        for notification in notifications:
            notification["_id"] = str(notification["_id"])
            notification["user_id"] = str(notification["user_id"])
            if notification.get("related_id"):
                notification["related_id"] = str(notification["related_id"])
        
        return {
            "notifications": notifications,
            "unread_count": len([n for n in notifications if not n.get("read", False)])
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
