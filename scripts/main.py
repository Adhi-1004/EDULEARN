"""
FastAPI application entry point
This file imports the app from the app module for backward compatibility
"""
from app.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=5001,
        reload=True
    )
