from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from typing import Optional
from ..services.socket_manager import socket_manager
from ..db import get_db
import jwt
import os
import logging
from bson import ObjectId

router = APIRouter()
logger = logging.getLogger(__name__)

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"

async def validate_token_ws(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        return user_id
    except Exception as e:
        logger.error(f"WebSocket auth failed: {e}")
        return None

@router.websocket("/ws/live/{batch_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, batch_id: str, user_id: str, token: str = Query(...)):
    # 1. Validate Token
    token_user_id = await validate_token_ws(token)
    
    if not token_user_id or token_user_id != user_id:
        # Close with policy violation if auth fails
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # 2. Accept Connection via Manager
    await socket_manager.connect(websocket, batch_id, user_id)
    
    try:
        # 3. Restore State (Crucial Step)
        # Fetch current live session state from DB
        try:
            db = await get_db()
            # Find active session for this batch
            # Assuming one active session per batch for now or derived from TimeSlot
            # For strictness, we might query by 'batch_id' and 'is_active' or similar. 
            # Per prompt: "LiveSession... active_content_payload... active_students"
            # We look for a LiveSession associated with a TimeSlot that is somewhat "current".
            # For simplicity in Phase 1 Foundation, we fetch by batch_id if we decide to store batch_id in LiveSession (I added it).
            live_session = await db.live_sessions.find_one(
                {"batch_id": batch_id, "current_state": {"$ne": "ENDED"}} # assuming ENDED or similar logic
                # Actually, models.py LiveSession has `current_state` enum. 'WAITING' is initial.
                # Only check logic if session exists.
            )
            
            if live_session:
                # Add user to active_students if not present
                if user_id not in live_session.get("active_students", []):
                     await db.live_sessions.update_one(
                        {"_id": live_session["_id"]},
                        {"$addToSet": {"active_students": user_id}}
                     )
                
                # Send current state
                state_message = {
                    "type": "STATE_RESTORE",
                    "payload": {
                        "current_state": live_session.get("current_state"),
                        "active_content": live_session.get("active_content_payload")
                    }
                }
                await websocket.send_json(state_message)
            else:
                # No active session found
                await websocket.send_json({"type": "INFO", "message": "No active live session."})

        except Exception as e:
            logger.error(f"Error fetching state for {user_id}: {e}")

        # 4. Listen loop
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages from client (e.g. "PONG", "ANSWER", "DOUBT")
            # For now, just logging or basic echoing/formatting
            # In Phase 4/5 we implement logic.
            # Example:
            # message = json.loads(data)
            # if message['type'] == 'DOUBT': ...
            pass

    except WebSocketDisconnect:
        socket_manager.disconnect(batch_id, user_id)
        # Optional: Remove from active_students in DB or mark as inactive?
        # Prompt says "real-time list of students joined". 
        # Usually we keep them in DB as "attended" but maybe remove from "online" list in UI via socket broadcast.
        await socket_manager.broadcast_to_batch(batch_id, {"type": "USER_LEFT", "user_id": user_id})

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        socket_manager.disconnect(batch_id, user_id)
