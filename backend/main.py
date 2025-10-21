"""
FastAPI Application Entry Point
This is the main entry point for the FastAPI application.
Run this from the backend directory to start the server.
"""
import sys
import os

# Add the current directory to Python path to resolve imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn

if __name__ == "__main__":
    print("Starting FastAPI server...")
    print("Server will be available at: http://0.0.0.0:5001")
    print("API documentation at: http://0.0.0.0:5001/docs")
    print("Press Ctrl+C to stop the server")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=5001,
        reload=True,
        log_level="info"
    )
