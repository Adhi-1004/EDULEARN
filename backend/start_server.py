#!/usr/bin/env python3
"""
Simple startup script for the FastAPI backend
This script ensures proper module resolution and starts the server.
"""
import sys
import os
import subprocess

def main():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Change to the backend directory
    os.chdir(script_dir)
    
    # Add current directory to Python path
    sys.path.insert(0, script_dir)
    
    print("🚀 Starting EDULEARN Backend Server...")
    print("📍 Backend directory:", script_dir)
    print("🌐 Server will be available at: http://0.0.0.0:5001")
    print("📚 API documentation at: http://0.0.0.0:5001/docs")
    print("🔍 Health check at: http://0.0.0.0:5001/health")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Start the server using uvicorn
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "5001",
            "--reload",
            "--log-level", "info"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

