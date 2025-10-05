"""
FastAPI Application Entry Point
This is the main entry point for the FastAPI application.
Run this from the backend directory to start the server.
"""
import uvicorn
from app.main import app

if __name__ == "__main__":
    print("Starting FastAPI server...")
    print("Server will be available at: http://localhost:5001")
    print("API documentation at: http://localhost:5001/docs")
    print("Press Ctrl+C to stop the server")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=5001,
        reload=True,
        log_level="info"
    )
