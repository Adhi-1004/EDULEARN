from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import logging

from ..db import get_db
from ..models.live_models import LiveSession, SessionState, LiveContent
from ..models.models import UserModel
from bson import ObjectId
from ..dependencies import get_current_user, require_teacher_or_admin
from ..services.socket_manager import socket_manager

router = APIRouter()
logger = logging.getLogger(__name__)

class StartSessionRequest(BaseModel):
    batch_id: str
    timeslot_id: Optional[str] = None

class EndSessionRequest(BaseModel):
    batch_id: str

@router.post("/start")
async def start_session(
    request: StartSessionRequest,
    current_user: UserModel = Depends(require_teacher_or_admin)
):
    """Start a live session for a batch"""
    db = await get_db()
    
    # 1. Check if session already active
    existing = await db.live_sessions.find_one({
        "batch_id": request.batch_id,
        "current_state": {"$ne": SessionState.ENDED}
    })
    
    if existing:
        return {"message": "Session already active", "session_id": str(existing["_id"])}
        
    # 2. Create new session
    # If timeslot_id provided, fetch content
    active_content = {}
    if request.timeslot_id:
        content = await db.live_content.find_one({"timeslot_id": request.timeslot_id})
        if content:
            # We don't load all content into 'active_payload' immediately, 
            # but we could link it. For now, we start empty.
            pass

    # Generate session code
    import random, string
    session_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    new_session = LiveSession(
        batch_id=request.batch_id,
        timeslot_id=request.timeslot_id or "ADHOC",
        started_at=datetime.utcnow(),
        session_code=session_code,
        current_state=SessionState.WAITING,
        active_students=[],
        active_content_payload={}
    )
    
    result = await db.live_sessions.insert_one(new_session.model_dump(by_alias=True, exclude={"id"}))
    
    # 3. Notify Students
    try:
        # Get Batch Name
        batch = await db.batches.find_one({"_id": ObjectId(request.batch_id)})
        batch_name = batch.get("name", "Class") if batch else "Class"
        
        # Get Topic Name from Timeslot if available
        topic_name = "Live Session"
        if request.timeslot_id:
            try:
                timeslot = await db.timeslots.find_one({"_id": ObjectId(request.timeslot_id)})
                if timeslot:
                    topic_name = timeslot.get("topic", "Live Session")
            except:
                pass
                
        # Find students in batch
        students = await db.users.find({"role": "student", "batch_ids": request.batch_id}).to_list(length=1000)
        
        if students:
            notifications = []
            for student in students:
                notifications.append({
                    "user_id": student["_id"],
                    "type": "live_class_start",
                    "title": f"🔴 Live Now: {topic_name}",
                    "message": f"{current_user.username or 'Teacher'} has started the live session for {batch_name}. Join now!",
                    "link": f"/student/live/{request.batch_id}",
                    "created_at": datetime.utcnow(),
                    "is_read": False,
                    "priority": "high"
                })
            
            if notifications:
                await db.notifications.insert_many(notifications)
                logger.info(f"Sent live class notifications to {len(notifications)} students")
                
    except Exception as e:
        logger.error(f"Failed to send notifications: {e}")
    
    logger.info(f"Session started for batch {request.batch_id} by {current_user.email}")
    return {"message": "Session started", "session_id": str(result.inserted_id)}

@router.post("/end")
async def end_session(
    request: EndSessionRequest,
    current_user: UserModel = Depends(require_teacher_or_admin)
):
    """End the live session and save attendance"""
    db = await get_db()
    
    # 1. Find active session
    session = await db.live_sessions.find_one({
        "batch_id": request.batch_id,
        "current_state": {"$ne": SessionState.ENDED}
    })
    
    if not session:
        raise HTTPException(status_code=404, detail="No active session found")
        
    # 2. Update to ENDED
    await db.live_sessions.update_one(
        {"_id": session["_id"]},
        {"$set": {
            "current_state": SessionState.ENDED,
            "end_time": datetime.utcnow()
        }}
    )
    
    # 3. Calculate Attendance
    # In a real app, we might save this to an 'Attendance' collection.
    # For now, we'll just log it or update the session document.
    active_students = session.get("active_students", [])
    logger.info(f"Session ended. Attendance count: {len(active_students)}")
    
    # 4. Broadcast END to sockets (optional, or let client handle disconnect)
    # await socket_manager.broadcast_to_batch(request.batch_id, {"type": "SESSION_ENDED"})
    
    return {
        "message": "Session ended successfully", 
        "duration_minutes": (datetime.utcnow() - session["started_at"]).total_seconds() / 60,
        "attendance_count": len(active_students)
    }

@router.get("/active-for-student")
async def get_active_sessions_for_student(
    current_user: UserModel = Depends(get_current_user)
):
    """Get active live sessions for the student's batches"""
    if current_user.role != "student":
        return {"active_sessions": []}
        
    db = await get_db()
    
    # 1. Get student's batches
    batch_ids = current_user.batch_ids or []
    if not batch_ids:
        return {"active_sessions": []}
        
    # 2. Find active sessions
    active_sessions = await db.live_sessions.find({
        "batch_id": {"$in": batch_ids},
        "current_state": {"$ne": SessionState.ENDED}
    }).to_list(length=10)
    
    result = []
    for session in active_sessions:
        # Get batch name
        batch = await db.batches.find_one({"_id": ObjectId(session["batch_id"])})
        batch_name = batch.get("name", "Class") if batch else "Class"
        
        result.append({
            "batch_id": session["batch_id"],
            "batch_name": batch_name,
            "session_code": session.get("session_code"),
            "started_at": session.get("started_at")
        })
        
    return {"active_sessions": result}
