"""
FastAPI Application Entry Point
Run the application from the backend directory
"""
import uvicorn
from app.main import app

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=5001,
        reload=True
    )
