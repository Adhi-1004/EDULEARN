"""
Notification endpoints
Handles system notifications, alerts, and communication
"""
from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

from ...core.security import security_manager
from ...db import get_db
from ...models.models import UserModel
from ...dependencies import get_current_user, require_admin

router = APIRouter()

# Request/Response Models
class NotificationCreate(BaseModel):
    title: str
    message: str
    type: str = Field(..., regex="^(info|warning|success|error)$")
    target_users: Optional[List[str]] = None  # User IDs, None for all users
    priority: str = Field("normal", regex="^(low|normal|high|urgent)$")

class NotificationResponse(BaseModel):
    notification_id: str
    title: str
    message: str
    type: str
    priority: str
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime] = None

class NotificationStats(BaseModel):
    total_notifications: int
    unread_count: int
    read_count: int
    by_type: Dict[str, int]
    by_priority: Dict[str, int]

@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    unread_only: bool = Query(False),
    type_filter: Optional[str] = Query(None, regex="^(info|warning|success|error)$"),
    priority_filter: Optional[str] = Query(None, regex="^(low|normal|high|urgent)$"),
    limit: int = Query(50, ge=1, le=100),
    current_user: UserModel = Depends(get_current_user)
):
    """Get user's notifications"""
    try:
        db = await get_db()
        
        # Build filter
        filter_dict = {"user_id": str(current_user.id)}
        if unread_only:
            filter_dict["is_read"] = False
        if type_filter:
            filter_dict["type"] = type_filter
        if priority_filter:
            filter_dict["priority"] = priority_filter
        
        # Get notifications
        notifications_cursor = db.notifications.find(filter_dict).sort("created_at", -1).limit(limit)
        notifications = []
        
        async for notification_doc in notifications_cursor:
            notifications.append(NotificationResponse(
                notification_id=str(notification_doc["_id"]),
                title=notification_doc["title"],
                message=notification_doc["message"],
                type=notification_doc["type"],
                priority=notification_doc["priority"],
                is_read=notification_doc["is_read"],
                created_at=notification_doc["created_at"],
                read_at=notification_doc.get("read_at")
            ))
        
        return notifications
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get notifications: {str(e)}"
        )

@router.post("/", response_model=NotificationResponse)
async def create_notification(
    notification: NotificationCreate,
    current_user: UserModel = Depends(require_admin)
):
    """Create a new notification (Admin only)"""
    try:
        db = await get_db()
        
        # Determine target users
        if notification.target_users:
            target_user_ids = notification.target_users
        else:
            # Send to all users
            users_cursor = db.users.find({}, {"_id": 1})
            target_user_ids = []
            async for user_doc in users_cursor:
                target_user_ids.append(str(user_doc["_id"]))
        
        # Create notification for each target user
        notifications_created = []
        for user_id in target_user_ids:
            notification_doc = {
                "user_id": user_id,
                "title": notification.title,
                "message": notification.message,
                "type": notification.type,
                "type": notification.type,  # Keep both for compatibility
                "priority": notification.priority,
                "is_read": False,
                "created_at": datetime.utcnow(),
                "created_by": str(current_user.id)
            }
            
            result = await db.notifications.insert_one(notification_doc)
            notification_doc["_id"] = result.inserted_id
            notifications_created.append(notification_doc)
        
        # Return the first notification as response
        first_notification = notifications_created[0]
        return NotificationResponse(
            notification_id=str(first_notification["_id"]),
            title=first_notification["title"],
            message=first_notification["message"],
            type=first_notification["type"],
            priority=first_notification["priority"],
            is_read=first_notification["is_read"],
            created_at=first_notification["created_at"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create notification: {str(e)}"
        )

@router.put("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """Mark notification as read"""
    try:
        db = await get_db()
        
        # Update notification
        result = await db.notifications.update_one(
            {"_id": notification_id, "user_id": str(current_user.id)},
            {"$set": {"is_read": True, "read_at": datetime.utcnow()}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        return {"message": "Notification marked as read"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark notification as read: {str(e)}"
        )

@router.put("/read-all")
async def mark_all_notifications_read(current_user: UserModel = Depends(get_current_user)):
    """Mark all notifications as read"""
    try:
        db = await get_db()
        
        # Update all user's unread notifications
        result = await db.notifications.update_many(
            {"user_id": str(current_user.id), "is_read": False},
            {"$set": {"is_read": True, "read_at": datetime.utcnow()}}
        )
        
        return {
            "message": f"Marked {result.modified_count} notifications as read"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark all notifications as read: {str(e)}"
        )

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """Delete a notification"""
    try:
        db = await get_db()
        
        # Delete notification
        result = await db.notifications.delete_one(
            {"_id": notification_id, "user_id": str(current_user.id)}
        )
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        return {"message": "Notification deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete notification: {str(e)}"
        )

@router.get("/stats", response_model=NotificationStats)
async def get_notification_stats(current_user: UserModel = Depends(get_current_user)):
    """Get notification statistics for current user"""
    try:
        db = await get_db()
        
        # Get user's notifications
        user_notifications = db.notifications.find({"user_id": str(current_user.id)})
        
        total_notifications = 0
        unread_count = 0
        read_count = 0
        by_type = {}
        by_priority = {}
        
        async for notification in user_notifications:
            total_notifications += 1
            
            if notification["is_read"]:
                read_count += 1
            else:
                unread_count += 1
            
            # Count by type
            notification_type = notification["type"]
            by_type[notification_type] = by_type.get(notification_type, 0) + 1
            
            # Count by priority
            priority = notification["priority"]
            by_priority[priority] = by_priority.get(priority, 0) + 1
        
        return NotificationStats(
            total_notifications=total_notifications,
            unread_count=unread_count,
            read_count=read_count,
            by_type=by_type,
            by_priority=by_priority
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get notification stats: {str(e)}"
        )

@router.post("/broadcast")
async def broadcast_notification(
    notification: NotificationCreate,
    current_user: UserModel = Depends(require_admin)
):
    """Broadcast notification to all users (Admin only)"""
    try:
        db = await get_db()
        
        # Get all active users
        users_cursor = db.users.find({"is_active": True}, {"_id": 1})
        user_ids = []
        async for user_doc in users_cursor:
            user_ids.append(str(user_doc["_id"]))
        
        # Create notification for each user
        notifications_created = 0
        for user_id in user_ids:
            notification_doc = {
                "user_id": user_id,
                "title": notification.title,
                "message": notification.message,
                "type": notification.type,
                "priority": notification.priority,
                "is_read": False,
                "created_at": datetime.utcnow(),
                "created_by": str(current_user.id)
            }
            
            await db.notifications.insert_one(notification_doc)
            notifications_created += 1
        
        return {
            "message": f"Notification broadcasted to {notifications_created} users",
            "recipients": notifications_created
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to broadcast notification: {str(e)}"
        )
