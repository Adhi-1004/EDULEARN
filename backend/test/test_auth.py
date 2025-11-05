#!/usr/bin/env python3
import asyncio
import json
from app.db import get_db, init_db
from app.core.security import security_manager

async def test_auth():
    try:
        await init_db()
        db = await get_db()
        
        # Get a teacher user
        teacher = await db.users.find_one({"role": "teacher"})
        if not teacher:
            print("No teacher found in database")
            return
        
        print(f"Found teacher: {teacher.get('email', 'Unknown')}")
        
        # Generate a token for the teacher
        token = security_manager.create_access_token(
            data={"sub": str(teacher["_id"]), "email": teacher["email"], "role": teacher["role"]}
        )
        
        print(f"Generated token: {token}")
        
        # Test the token
        try:
            from fastapi.security import HTTPAuthorizationCredentials
            credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
            payload = security_manager.verify_token(credentials)
            print(f"Token payload: {payload}")
        except Exception as e:
            print(f"Token verification failed: {e}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_auth())
